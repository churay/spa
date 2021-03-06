__doc__ = '''Module for the Image Processing Functionality'''

import sys, colorsys, collections
import spa
from vector import vector

# TODO(JRC): Do an audit of the names in this function and make improvements
# where necessary.

### Module Functions ###

## Color Functions ##

def is_opaque(pixel, image):
    return image.getpixel(to_2d(pixel, image))[3] != 0

def distrib_colors(count):
    hues = [(1.0/count)*i for i in range(count)]
    rgbs = [colorsys.hsv_to_rgb(h, 1.0, 1.0) for h in hues]
    return [tuple(int(cc*255) for cc in c) for c in rgbs]

## Math Functions ##

def to_1d(*args, **kwargs):
    is_tuple_call = isinstance(args[0], tuple)
    pixel = args[0] if is_tuple_call else tuple(args[0:2])
    image = args[1] if is_tuple_call else args[2]
    as_vector = args[3 - int(is_tuple_call)] if len(args) > 3 - int(is_tuple_call) \
        else kwargs.get('as_vector', False)

    pixel_1d = pixel[0] + pixel[1] * image.width
    return vector(1, pixel_1d) if as_vector else pixel_1d

def to_2d(*args, **kwargs):
    pixel = args[0]
    image = args[1]
    as_vector = args[2] if len(args) > 2 \
        else kwargs.get('as_vector', False)

    pixel_2d = (int(pixel % image.width), int(pixel / image.width))
    return vector(2, *pixel_2d) if as_vector else pixel_2d

def to_pixel(vector):
    return tuple(int(vector[d]) for d in range(vector.dim))

def calc_adjacent(pixel, image):
    px, py = to_2d(pixel, image)
    return [
        to_1d(px+dx, py+dy, image) for dx in range(-1, 2) for dy in range(-1, 2)
        if 0 <= px+dx < image.width and 0 <= py+dy < image.height
        and to_1d(px+dx, py+dy, image) != pixel]

# TODO(JRC): Consider adding support for alignment by percentages as well.
def calc_alignment(align_coords, image, subimage=None):
    out_coords = vector(2, 0)

    for align_index, align_coord in enumerate(align_coords.dvals):
        if align_coord == spa.align.lo:
            out_coords[align_index] = 0
        elif align_coord == spa.align.mid:
            image_coord = image.size[align_index] / 2
            subimage_adjust = subimage.size[align_index] / 2 if subimage else 0
            out_coords[align_index] = image_coord - subimage_adjust
        elif align_coord == spa.align.hi:
            image_coord = image.size[align_index] - 1
            subimage_adjust = subimage.size[align_index] if subimage else 0
            out_coords[align_index] = image_coord - subimage_adjust
        else:
            out_coords[align_index] = align_coord

    return out_coords

# TODO(JRC): This algorithm implements the "Shoelace Formula," which I should
# learn how to prove works to myself.
def calc_orientation(boundary, image):
    bound_orient = None

    if boundary[0] not in calc_adjacent(boundary[-1], image):
        bound_orient = spa.orient.none
    else:
        boundary_2d = [to_2d(bp, image) for bp in boundary]
        boundary_shoelace = zip(boundary_2d, boundary_2d[1:] + [boundary_2d[0]])
        boundary_orient = (
            sum(p0[0]*p1[1] for p0, p1 in boundary_shoelace) -
            sum(p1[0]*p0[1] for p0, p1 in boundary_shoelace))
        bound_orient = spa.orient.cw if boundary_orient < 0 else spa.orient.ccw

    return bound_orient

# TODO(JRC): Improve this method by using a neighborhood curve approximation
# technique based on point fitting.
def calc_tangent(boundary, index, image):
    tangent_samples = [
        to_2d(boundary[(index+i)%len(boundary)], image, True) - \
        to_2d(boundary[(index-i)], image, True) for i in range(1, 5)]

    tangent_average = sum(tangent_samples, vector(2, 0.0)) / len(tangent_samples)
    tangent_average.inormal()

    return tangent_average

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

def calc_connected_bbox(image, component):
    component_2d = [to_2d(p, image) for p in component]

    component_min = tuple(min(p[d] for p in component_2d) for d in range(2))
    component_max = tuple(max(p[d] for p in component_2d) for d in range(2))

    return (component_min[0], component_min[1],
        component_max[0]-component_min[0], component_max[1]-component_min[1])

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
    # TODO(JRC): Change this method to be an iterative method so that this
    # weird adjustment of the recursion limit isn't necessary.
    sys.setrecursionlimit(5000)

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

            stroke_list.append(stroke_pixels)
        strokes.append(stroke_list)

    return strokes

def orient_cell_strokes(image, orient_image, strokes):
    assert image.size == orient_image.size, 'The given image sizes do not match.'

    oriented_strokes = []

    stroke_orient_pixels = [
        next((p for p in s if is_opaque(p, orient_image)), None)
        for s in strokes]

    # TODO(JRC): Add a check here that ensures that all of the non-opaque
    # pixels are used in the given 'orient_image'.

    for stroke, orient_pixel in zip(strokes, stroke_orient_pixels):
        oriented_stroke = stroke
        if orient_pixel:
            orient_index = stroke.index(orient_pixel)
            for shift_index, shift_value in \
                    enumerate(stroke[orient_index:] + stroke[:orient_index]):
                oriented_stroke[shift_index] = shift_value

            orient_alpha = orient_image.getpixel(to_2d(orient_pixel, orient_image))[3]
            want_orient = spa.orient.cw if orient_alpha == 255 else spa.orient.ccw
            curr_orient = calc_orientation(oriented_stroke, image)
            if curr_orient != want_orient : oriented_stroke.reverse()
        oriented_strokes.append(oriented_stroke)

    return oriented_strokes

def order_cell_strokes(image, orient_image, strokes):
    # TODO(JRC): There are still bugs in this code when grouping the pixels
    # into bins.
    assert image.size == orient_image.size, 'The given image sizes do not match.'

    stroke_orient_pixels = [
        next((p for p in s if is_opaque(p, orient_image)), None)
        for s in strokes]

    # TODO(JRC): Add a check here that ensures that all of the non-opaque
    # pixels are used in the given 'orient_image'.

    orient_color_to_strokes = collections.defaultdict(list)
    orient_extra_strokes = []
    for stroke, orient_pixel in zip(strokes, stroke_orient_pixels):
        if orient_pixel:
            orient_color = orient_image.getpixel(to_2d(orient_pixel, orient_image))[:3]
            orient_color_to_strokes[orient_color].append(stroke)
        else:
            orient_extra_strokes.append(stroke)

    # TODO(JRC): Improve this behavior if default binning missing strokes
    # becomes important in the future.
    orient_color_to_strokes[orient_color_to_strokes.keys()[0]].extend(orient_extra_strokes)

    ordered_strokes = [orient_color_to_strokes[c] for c in
        sorted(orient_color_to_strokes.keys(),
        key=lambda c: colorsys.rgb_to_hsv(*c)[::-1] if c else (1.0, 1.0, 1.0))]

    return ordered_strokes
