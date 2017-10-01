#!/usr/bin/env python

__doc__ = '''Module for "SPA" Console Application'''

import os, optparse, collections, colorsys
import spa
from PIL import Image

### Main Entry Point ###

def main():
    ## Program Constants ##

    base_dir = os.path.dirname(os.path.realpath(__file__))
    input_dir = os.path.join(base_dir, 'in')
    output_dir = os.path.join(base_dir, 'out')

    # TODO(JRC): This code currently assumes that the default boundary calculation
    # function was used when performing caching. This will need to be changed if more
    # schemes are ever introduced.
    use_caching = True

    ## Factored Functionality ##

    def to_1d(px, py, img): return px + py * img.width
    def to_2d(pi, img):     return (int(pi % img.width), int(pi / img.width))

    def calc_adjacent(pixel, image):
        px, py = to_2d(pixel, image)
        return [
            to_1d(px+dx, py+dy, image) for dx in range(-1, 2) for dy in range(-1, 2)
            if 0 <= px+dx < image.width and 0 <= py+dy < image.height
            and to_1d(px+dx, py+dy, image) != pixel]

    def is_opaque(pixel, image):
        return image.getpixel(to_2d(pixel, image))[3] != 0

    # NOTE(JRC): Modify this function to redefine what it means for adjacent
    # pixels in a given image to be members of different components.
    def is_component_boundary(curr_pixel, next_pixel, image):
        curr_alpha = image.getpixel(to_2d(curr_pixel, image))[3]
        next_alpha = image.getpixel(to_2d(next_pixel, image))[3]
        return curr_alpha * next_alpha == 0 and curr_alpha + next_alpha != 0

    # TODO(JRC): Consider cleaning up all of this caching code by introducing
    # a decorator that wraps each function and allows custom saving behavior
    # to be defined.
    def get_cache_path(image, cache_type):
        image_filename = os.path.basename(image.filename)
        image_name, image_ext = os.path.splitext(image_filename)
        return os.path.join(output_dir,
            '{0}_{1}{2}'.format(image_name, cache_type, image_ext))

    def distrib_colors(count):
        hues = [(1.0/count)*i for i in range(count)]
        rgbs = [colorsys.hsv_to_rgb(h, 1.0, 1.0) for h in hues]
        return [tuple(int(cc*255) for cc in c) for c in rgbs]

    def calc_components(image, is_valid=is_opaque, is_boundary=is_component_boundary):
        if use_caching and os.path.isfile(get_cache_path(image, 'comps')):
            cache_image = Image.open(get_cache_path(image, 'comps'))
            components = collections.defaultdict(list)
            for pixel in range(cache_image.width * cache_image.height):
                if is_opaque(pixel, cache_image):
                    color = cache_image.getpixel(to_2d(pixel, cache_image))
                    components[color].append(pixel)
            return components.values()

        components = []

        visited_pixels = set()
        for curr_pixel in range(image.width * image.height):
            if is_valid(curr_pixel, image) and curr_pixel not in visited_pixels:
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
                            not is_boundary(component_pixel, adj_pixel, image))

                components.append(component)

        if use_caching:
            cache_image = Image.new('RGBA', image.size, color=(0, 0, 0, 0))
            component_colors = distrib_colors(len(components))
            for component, color in zip(components, component_colors):
                for pixel in component:
                    cache_image.putpixel(to_2d(pixel, cache_image), color)
            cache_image.save(get_cache_path(image, 'comps'))

        return components

    def calc_boundaries(image, components, is_boundary=is_component_boundary):
        if use_caching and os.path.isfile(get_cache_path(image, 'bounds')):
            cache_image = Image.open(get_cache_path(image, 'bounds'))
            boundaries = collections.defaultdict(lambda: collections.defaultdict(list))
            for pixel in range(cache_image.width * cache_image.height):
                if is_opaque(pixel, cache_image):
                    color = cache_image.getpixel(to_2d(pixel, cache_image))
                    boundaries[color[:3]][color[3]].append(pixel)
            return [b.values() for b in boundaries.values()]

        boundaries = []

        for component in components:
            boundary_list = []
            boundary_pixels = set(cp for cp in component if
                any(is_boundary(cp, ap, image) for ap in calc_adjacent(cp, image)))

            visited_pixels = set()
            for bound_pixel in boundary_pixels:
                if bound_pixel not in visited_pixels:
                    boundary = []

                    pending_pixels = [bound_pixel]
                    while pending_pixels:
                        pending_pixel = pending_pixels.pop()
                        if pending_pixel not in visited_pixels:
                            visited_pixels.add(pending_pixel)
                            boundary.append(pending_pixel)

                            adj_pixels = set(calc_adjacent(pending_pixel, image))
                            pending_pixels.extend(list(adj_pixels & boundary_pixels))

                    boundary_list.append(boundary)

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

    # TODO(JRC): When stroking the boundaries for all of the silhouettes, use
    # graph distance instead of pixel distance for the fill to prevent artifacting
    # on some silhouettes (e.g. the e).
    def calc_strokes():
        pass

    ## Script Processing ##

    base_image = Image.open(os.path.join(input_dir, 'silhouette_small.png'))#'silhouette.png'))#'test.png'))
    over_image = Image.open(os.path.join(input_dir, 'overlay.png'))
    # TODO(JRC): Scale this image based on the scaling factor that will
    # be used for the pop effect.
    out_image = Image.new('RGBA', base_image.size, color=(255, 255, 255, 255))

    # TODO(JRC): This is the full loading functionality, which only needs to
    # be re-run when there are changes to the base image.
    base_components = calc_components(base_image)
    base_boundaries = calc_boundaries(base_image, base_components)
    base_colors = distrib_colors(len(base_components))

    # base_boundaries = calc_boundaries(base_image, [])
    # base_colors = distrib_colors(len(base_boundaries))

    '''
    for component, color in zip(base_components, base_colors):
        for component_pixel in component:
            out_image.putpixel(to_2d(component_pixel, out_image), color)
    '''

    for boundaries, color in zip(base_boundaries, base_colors):
        for boundary in boundaries:
            for boundary_pixel in boundary:
                out_image.putpixel(to_2d(boundary_pixel, out_image), color)

    out_image.save(os.path.join(output_dir, 'test.png'))

### Miscellaneous ###

if __name__ == '__main__':
    main()
