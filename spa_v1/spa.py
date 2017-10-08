#!/usr/bin/env python

__doc__ = '''Module for "SPA" Console Application'''

import os, sys, optparse, collections, colorsys
import spa
from PIL import Image

### Main Entry Point ###

def main():
    ## Program Constants ##

    # TODO(JRC): This code currently assumes that the default boundary calculation
    # function was used when performing caching. This will need to be changed if more
    # schemes are ever introduced.
    use_caching = True

    ## Factored Functionality ##

    # Caching/File Functions #

    # TODO(JRC): Consider cleaning up all of this caching code by introducing
    # a decorator that wraps each function and allows custom saving behavior
    # to be defined.
    def get_cache_path(image, cache_type):
        image_filename = os.path.basename(image.filename)
        image_name, image_ext = os.path.splitext(image_filename)
        return os.path.join(spa.output_dir,
            '{0}_{1}{2}'.format(image_name, cache_type, image_ext))

    # Basic Image Functions #

    def to_1d(px, py, img): return px + py * img.width
    def to_2d(pi, img):     return (int(pi % img.width), int(pi / img.width))

    def calc_adjacent(pixel, image):
        px, py = to_2d(pixel, image)
        return [
            to_1d(px+dx, py+dy, image) for dx in range(-1, 2) for dy in range(-1, 2)
            if 0 <= px+dx < image.width and 0 <= py+dy < image.height
            and to_1d(px+dx, py+dy, image) != pixel]

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

    # Color Functions #

    def is_opaque(pixel, image):
        return image.getpixel(to_2d(pixel, image))[3] != 0

    def distrib_colors(count):
        hues = [(1.0/count)*i for i in range(count)]
        rgbs = [colorsys.hsv_to_rgb(h, 1.0, 1.0) for h in hues]
        return [tuple(int(cc*255) for cc in c) for c in rgbs]

    # Advanced Image Functions #

    # NOTE(JRC): A cell is defined to be a collection of pixels that are
    # completely transparent (alpha == 0) or opaque (alpha != 0).
    def is_cell_boundary(curr_pixel, next_pixel, image):
        curr_alpha = image.getpixel(to_2d(curr_pixel, image))[3]
        next_alpha = image.getpixel(to_2d(next_pixel, image))[3]
        return curr_alpha * next_alpha == 0 and curr_alpha + next_alpha != 0

    def calc_opaque_cells(image):
        if use_caching and os.path.isfile(get_cache_path(image, 'comps')):
            cache_image = Image.open(get_cache_path(image, 'comps'))
            cells = collections.defaultdict(list)
            for pixel in range(cache_image.width * cache_image.height):
                if is_opaque(pixel, cache_image):
                    color = cache_image.getpixel(to_2d(pixel, cache_image))
                    cells[color].append(pixel)
            return cells.values()

        opaque_pixels = set(p for p in range(image.width * image.height) if
            is_opaque(p, image))

        cells = calc_connected_components(image, opaque_pixels,
            lambda cp, ap, i: not is_cell_boundary(cp, ap, i))

        if use_caching:
            cache_image = Image.new('RGBA', image.size, color=(0, 0, 0, 0))
            cell_colors = distrib_colors(len(cells))
            for cell, color in zip(cells, cell_colors):
                for pixel in cell:
                    cache_image.putpixel(to_2d(pixel, cache_image), color)
            cache_image.save(get_cache_path(image, 'comps'))

        return cells

    def calc_cell_boundaries(image, cells):
        if use_caching and os.path.isfile(get_cache_path(image, 'bounds')):
            cache_image = Image.open(get_cache_path(image, 'bounds'))
            boundaries = collections.defaultdict(lambda: collections.defaultdict(list))
            for pixel in range(cache_image.width * cache_image.height):
                if is_opaque(pixel, cache_image):
                    color = cache_image.getpixel(to_2d(pixel, cache_image))
                    boundaries[color[:3]][color[3]].append(pixel)
            return [b.values() for b in boundaries.values()]

        boundaries = []

        for cell in cells:
            boundary_pixels = set(cp for cp in cell if
                any(is_cell_boundary(cp, ap, image) for ap in calc_adjacent(cp, image)))

            boundary_list = calc_connected_components(image, boundary_pixels,
                lambda cp, ap, i: True)
            boundaries.append(boundary_list)

        if use_caching:
            cache_image = Image.new('RGBA', image.size, color=(0, 0, 0, 0))
            boundary_colors = distrib_colors(len(boundaries))
            for boundary_list, color in zip(boundaries, boundary_colors):
                boundary_alphas = [
                    int((1.0/len(boundary_list))*255*i) for i in
                    range(len(boundary_list), 0, -1)]
                for boundary, alpha in zip(boundary_list, boundary_alphas):
                    color_alpha = (color[0], color[1], color[2], alpha)
                    for pixel in boundary:
                        cache_image.putpixel(to_2d(pixel, cache_image), color_alpha)
            cache_image.save(get_cache_path(image, 'bounds'))

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
                sorted_adj_pixels = sorted(list(adj_pixels), reverse=False, key=lambda p:
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

                start_pixel, next_pixel, end_pixel = None, None, None
                for bound_pixel in boundary:
                    adj_pixels = set(calc_adjacent(bound_pixel, image)) & boundary_set
                    adj_sides = calc_connected_components(image, adj_pixels,
                        lambda cp, ap, i: cp != bound_pixel and ap != bound_pixel)

                    if len(adj_sides) > 1:
                        start_pixel = bound_pixel
                        next_pixel, end_pixel = adj_sides[0][0], adj_sides[1][0]
                assert start_pixel, 'Failed to calculate stroke start position.'

                visited_pixels = set([start_pixel])
                stroke_pixels = find_best_stroke(next_pixel, end_pixel,
                    visited_pixels, boundary_set) + [start_pixel]
                assert stroke_pixels is not None, 'Failed to calculate stroke(s).'

                stroke_list.append(stroke_pixels)
            strokes.append(stroke_list)

        return strokes

    ## Script Processing ##

    # TODO(JRC): Change 'find_best_stroke' above into an iterative method so that
    # this isn't necessary.
    sys.setrecursionlimit(5000)

    base_image = Image.open(os.path.join(spa.input_dir, 'test2.png'))#'basic.png'))#'silhouette_small.png'))#'silhouette.png'))
    over_image = Image.open(os.path.join(spa.input_dir, 'overlay.png'))

    # TODO(JRC): This is the full loading functionality, which only needs to
    # be re-run when there are changes to the base image.
    base_cells = calc_opaque_cells(base_image)
    base_boundaries = calc_cell_boundaries(base_image, base_cells)
    base_strokes = calc_cell_strokes(base_image, base_boundaries)
    base_colors = distrib_colors(len(base_cells))

    # TODO(JRC): Complete the following tasks to reach the stencil stroke capability:
    # - Fill in each boundary sequentially to make the movie.
    # - Fill in each boundary on a time frame to make the movie (1 pixel per frame).
    # - Add the ability to fill in using an arbitrary stencil (requires implementing
    #   things like tangent detection, stencil specs, etc.)

    # TODO(JRC): Scale this image based on the scaling factor that will
    # be used for the pop effect.
    out_image = Image.new('RGBA', base_image.size, color=(255, 255, 255, 255))

    # TODO(JRC): When stroking the boundaries for all of the silhouettes, use
    # graph distance instead of pixel distance for the fill to prevent artifacting
    # on some silhouettes (e.g. the e).
    out_frames = [out_image.copy()]
    for base_stroke in [bs for bsl in base_strokes for bs in bsl]:
        for stroke_pixel in base_stroke:
            out_frame = out_frames[-1].copy()
            out_frame.putpixel(to_2d(stroke_pixel, out_image), (0, 0, 0, 255))
            out_frames.append(out_frame)

    assert spa.render_movie('test', out_frames, fps=600), 'Failed to render movie.'

    '''
    for cell, color in zip(base_cells, base_colors):
        for cell_pixel in cell:
            out_image.putpixel(to_2d(cell_pixel, out_image), color)
    '''

    '''
    for boundary_list, color in zip(base_boundaries, base_colors):
        for boundary in boundary_list:
            for boundary_pixel in boundary:
                out_image.putpixel(to_2d(boundary_pixel, out_image), color)
    '''

    # out_image.save(os.path.join(spa.output_dir, 'test.png'))

### Miscellaneous ###

if __name__ == '__main__':
    main()
