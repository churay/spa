__doc__ = '''Module for the Image Processing Functionality'''

import colorsys
import spa

# TODO(JRC): Do an audit of the names in this function and make improvements
# where necessary.

### Module Functions ###

## Color Functions ##

def is_opaque(pixel, image):
    return image.getpixel(to_2d(pixel, image))[3] != 0

def is_magenta(pixel, image):
    return image.getpixel(to_2d(pixel, image))[:3] == (255, 0, 255)

def distrib_colors(count):
    hues = [(1.0/count)*i for i in range(count)]
    rgbs = [colorsys.hsv_to_rgb(h, 1.0, 1.0) for h in hues]
    return [tuple(int(cc*255) for cc in c) for c in rgbs]

## Math Functions ##

def to_1d(pixel_x, pixel_y, image):
    return pixel_x + pixel_y * image.width

def to_2d(pixel_i, image):
    return (int(pixel_i % image.width), int(pixel_i / image.width))

def calc_adjacent(pixel, image):
    px, py = to_2d(pixel, image)
    return [
        to_1d(px+dx, py+dy, image) for dx in range(-1, 2) for dy in range(-1, 2)
        if 0 <= px+dx < image.width and 0 <= py+dy < image.height
        and to_1d(px+dx, py+dy, image) != pixel]

def is_cell_boundary(curr_pixel, next_pixel, image):
    curr_alpha = image.getpixel(to_2d(curr_pixel, image))[3]
    next_alpha = image.getpixel(to_2d(next_pixel, image))[3]
    return curr_alpha * next_alpha == 0 and curr_alpha + next_alpha != 0

## Processing Functions ##

def calc_connected_components(image, pixel_set, are_adjacent):
    components = []

    visited_pixels = set()
    for curr_pixel in pixel_set:
        if curr_pixel not in visited_pixels:
            component = []

            component_pixels = [curr_pixel]
            while component_pixels:
                component_pixel = component_pixels.pop()
                if component_pixel not in visited_pixels:
                    visited_pixels.add(component_pixel)
                    component.append(component_pixel)

                    adj_pixels = calc_adjacent(component_pixel, image)
                    component_pixels.extend(
                        adj_pixel for adj_pixel in adj_pixels if
                        (adj_pixel in pixel_set and
                        are_adjacent(component_pixel, adj_pixel, image)))

            components.append(component)

    return components

@spa.cache('comps')
def calc_opaque_cells(image):
    opaque_pixels = set(p for p in range(image.width * image.height) if
        is_opaque(p, image))
    return calc_connected_components(image, opaque_pixels,
        lambda cp, ap, i: not is_cell_boundary(cp, ap, i))

@spa.cache('bounds')
def calc_cell_boundaries(image, cells):
    boundaries = []

    for cell in cells:
        boundary_pixels = set(cp for cp in cell if
            any(is_cell_boundary(cp, ap, image) for ap in calc_adjacent(cp, image)))

        boundary_list = calc_connected_components(image, boundary_pixels,
            lambda cp, ap, i: True)
        boundaries.append(boundary_list)

    return boundaries

def calc_cell_strokes(image, boundaries):
    # TODO(JRC): Comb over this function again during refactoring and
    # trim down all of the excessively long lines.
    def find_best_stroke(curr_pixel, end_pixel, visited_pixels, stroke_pixels):
        visited_pixels.add(curr_pixel)

        if curr_pixel == end_pixel:
            return [curr_pixel]
        else:
            adj_pixels = set(calc_adjacent(curr_pixel, image)) & stroke_pixels
            adj_pixels -= visited_pixels
            sorted_adj_pixels = sorted(list(adj_pixels), reverse=True, key=lambda p:
                len([ap for ap in calc_adjacent(p, image) if is_cell_boundary(p, ap, image)]))

            for adj_pixel in sorted_adj_pixels:
                adj_stroke = find_best_stroke(adj_pixel, end_pixel, visited_pixels, stroke_pixels)
                if adj_stroke is not None: return adj_stroke + [curr_pixel]
            return None

    # TODO(JRC): This is calculated using the shoelace formula, which I
    # should read more about to understand how it works.
    def calc_stroke_orient(stroke):
        stroke_2d = [to_2d(sp, image) for sp in stroke]
        stroke_zip = zip(stroke_2d, stroke_2d[1:] + [stroke_2d[0]])

        stroke_orient = sum(p0[0]*p1[1] for p0, p1 in stroke_zip) - \
            sum(p1[0]*p0[1] for p0, p1 in stroke_zip)
        return stroke_orient < 0

    strokes = []

    for boundary_list in boundaries:
        stroke_list = []
        for boundary in boundary_list:
            boundary_set = set(boundary)

            start_pixels = []
            end_pixel = None
            for bound_pixel in boundary:
                adj_pixels = set(calc_adjacent(bound_pixel, image)) & boundary_set
                adj_sides = calc_connected_components(image, adj_pixels,
                    lambda cp, ap, i: not set([cp, ap]) & set([bound_pixel]))

                if len(adj_sides) > 1:
                    start_pixels.extend([bound_pixel, adj_sides[0][0]])
                    end_pixel = adj_sides[1][0]
                    break
                elif len(adj_sides) == 1:
                    retry_sides_list = []
                    for adj_pixel in adj_pixels:
                        retry_pixels = adj_pixels - set([adj_pixel])
                        retry_sides = calc_connected_components(image, retry_pixels,
                            lambda cp, ap, i: not set([cp, ap]) & set([bound_pixel, adj_pixel]))
                        retry_sides_list.append((adj_pixel, retry_sides))

                    retry_sides_list = sorted(retry_sides_list , reverse=True,
                        key=lambda p: len(p[1]))
                    if any(len(s) > 1 for p, s in retry_sides_list):
                        retry_pixel, retry_sides = retry_sides_list[0]
                        start_pixels.extend([bound_pixel, retry_pixel, retry_sides[0][0]])
                        end_pixel = retry_sides[1][0]
                        break
            assert start_pixels, 'Failed to calculate stroke start position.'

            visited_pixels = set(start_pixels)
            stroke_pixels = find_best_stroke(start_pixels[-1], end_pixel,
                visited_pixels, boundary_set)
            assert stroke_pixels is not None, 'Failed to calculate stroke(s).'
            stroke_pixels.extend(start_pixels[:-1][::-1])

            orient_pixel = next((p for p in stroke_pixels if is_magenta(p, image)), None)
            if orient_pixel:
                orient_index = stroke_pixels.index(orient_pixel)
                stroke_pixels = stroke_pixels[orient_index:] + stroke_pixels[:orient_index]

                orient_dir = image.getpixel(to_2d(orient_pixel, image))[3] == 255
                curr_dir = calc_stroke_orient(stroke_pixels)
                if orient_dir != curr_dir: stroke_pixels.reverse()

            stroke_list.append(stroke_pixels)
        strokes.append(stroke_list)

    return strokes