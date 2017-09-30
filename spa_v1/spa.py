#!/usr/bin/env python

__doc__ = '''Module for "SPA" Console Application'''

import os, optparse
import spa
from PIL import Image

### Main Entry Point ###

def main():
    ## Program Constants ##

    base_dir = os.path.dirname(os.path.realpath(__file__))
    input_dir = os.path.join(base_dir, 'img')
    output_dir = os.path.join(base_dir, 'out')

    silhouette_image = Image.open(os.path.join(input_dir, 'silhouette.png'))
    #overlay_image = Image.open(os.path.join(input_dir, 'overlay.png'))

    # TODO(JRC): Scale this image based on the scaling factor that will
    # be used for the pop effect.
    base_image = Image.new('RGBA', silhouette_image.size, color=(255, 255, 255, 255))

    ## Identify Connected Components ##

    # TODO(JRC): Generalize this code so that it isn't reliant on full alpha
    # pixels to define boundaries between image components.
    # TODO(JRC): Add caching capabilities to the calc functions so that an
    # image can have its path data trivially saved and loaded for quicker
    # turnaround times on recomputation.
    # TODO(JRC): When stroking the boundaries for all of the silhouettes, use
    # graph distance instead of pixel distance for the fill to prevent artifacting
    # on some silhouettes (e.g. the e).

    def to_1d(px, py, img): return px + py * img.width
    def to_2d(pi, img):     return (int(pi % img.width), int(pi / img.width))

    def calc_adjacent(pixel, image):
        px, py = to_2d(pixel, image)
        return [
            to_1d(px+dx, py+dy, image) for dx in range(-1, 2) for dy in range(-1, 2)
            if 0 <= px+dx < image.width and 0 <= py+dy < image.height
            and to_1d(px+dx, py+dy, image) != pixel]

    # NOTE(JRC): Modify this function to redefine what it means for adjacent
    # pixels in a given image to be members of different components.
    def is_component_boundary(curr_pixel, next_pixel, image):
        curr_alpha = image.getpixel(to_2d(curr_pixel, image))[3]
        next_alpha = image.getpixel(to_2d(next_pixel, image))[3]
        return curr_alpha * next_alpha == 0 and curr_alpha + next_alpha != 0

    def calc_components(image, is_boundary=is_component_boundary):
        pixel_count = image.width * image.height
        component_dsets = spa.dsets(pixel_count)

        for curr_pixel in range(pixel_count):
            spa.display_status('pixel', curr_pixel, pixel_count)
            adj_pixels = calc_adjacent(curr_pixel, image)

            for adj_pixel in adj_pixels:
                if not is_boundary(curr_pixel, adj_pixel, image):
                    component_dsets.union(curr_pixel, adj_pixel)

        return component_dsets.tabulate().values()

    # TODO(JRC): Fix a bug in the boundary calculation function that prevents
    # a singular path from being formed due to eager assignment of parents and
    # step counts (preemptively searched in both directions before taking a path,
    # which wouldn't happen in a strictly DFS).

    # TODO(JRC): Return the boundaries as multiple lists where each list contains
    # an ordered sequence of pixels that constitutes a full path (the last value
    # is adjacent to the first value and each subsequent value is adjacent and
    # exactly one value away).
    def calc_boundaries(component, image):
        return []

    silhouette_components = calc_components(silhouette_image)
    #silhouette_boundaries = [calc_boundaries(silhouette_components[0], silhouette_image)]
    # silhouette_boundaries = [calc_boundaries(sc, silhouette_image) for sc in silhouette_components]

    color_list = [
        (255, 0, 0, 255), (255, 127, 0, 255), (255, 255, 0, 255),
        (0, 255, 0, 255), (0, 0, 255, 255), (75, 0, 130, 255),
        (148, 0, 211, 255)]

    '''
    for boundary_idx, boundary in enumerate(silhouette_boundaries):
        boundary_color = color_list[min(boundary_idx, len(color_list)-1)]
        for boundary_pixel in boundary:
            base_image.putpixel(boundary_pixel, boundary_color)
    '''

    for component_idx, component in enumerate(silhouette_components):
        component_color = color_list[min(component_idx, len(color_list)-1)]
        for component_pixel in component:
            base_image.putpixel(to_2d(component_pixel, base_image), component_color)

    base_image.save(os.path.join(output_dir, 'test.png'))

### Miscellaneous ###

if __name__ == '__main__':
    main()
