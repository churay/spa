#!/usr/bin/env python

__doc__ = '''Module for "SPA" Console Application'''

import os, optparse
from PIL import Image

### Main Entry Point ###

def main():
    ## Program Constants ##

    base_dir = os.path.dirname(os.path.realpath(__file__))
    input_dir = os.path.join(base_dir, 'img')
    output_dir = os.path.join(base_dir, 'out')

    silhouette_image = Image.open(os.path.join(input_dir, 'basic.png')) #'silhouette.png'))
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

    def is_empty(pixel, image):
        return image.getpixel(pixel)[3] == 0

    def calc_adjacent(pixel, image, only_nonempty):
        px, py = pixel
        return [
            (px+dx, py+dy) for dx in range(-1, 2) for dy in range(-1, 2)
            if 0 <= px+dx < image.width and 0 <= py+dy < image.height and dx+dy != 0
            and not (only_nonempty and is_empty((px+dx,py+dy), image))]

    def calc_components(image):
        components = []

        visited_pixels = {}
        pending_pixels = [((x, y),-1) for y in range(image.height) for x in range(image.width)]
        while pending_pixels:
            pending_pixel, pending_comp = pending_pixels.pop()

            if pending_pixel not in visited_pixels and not is_empty(pending_pixel, image):
                # NOTE(JRC): If this pixel doesn't have a component yet, then
                # this it's the first pixel in a new component.
                if pending_comp == -1:
                    pending_comp = len(components)
                    components.append([])

                component = components[pending_comp]
                component.append(pending_pixel)
                visited_pixels[pending_pixel] = pending_comp

                adjacent_pixels = calc_adjacent(pending_pixel, image, False)
                pending_pixels.extend(zip(adjacent_pixels, [pending_comp]*8))

        return components

    # TODO(JRC): Fix a bug in the boundary calculation function that prevents
    # a singular path from being formed due to eager assignment of parents and
    # step counts (preemptively searched in both directions before taking a path,
    # which wouldn't happen in a strictly DFS).

    # TODO(JRC): Return the boundaries as multiple lists where each list contains
    # an ordered sequence of pixels that constitutes a full path (the last value
    # is adjacent to the first value and each subsequent value is adjacent and
    # exactly one value away).
    def calc_boundaries(component, image):
        boundaries = []

        # TODO(JRC): We're currently only locating the outer boundary and ignoring
        # the inner (important for the o and the n).
        visited_steps, visited_parents = {}, {component[0]: None}
        pending_pixels = [(component[0], 0)]
        while pending_pixels:
            pending_pixel, pending_steps = pending_pixels.pop()
            adjacent_all = calc_adjacent(pending_pixel, image, False)

            if (any(is_empty(ap, image) for ap in adjacent_all) and
                    pending_steps < visited_steps.get(pending_pixel, float('inf'))):
                adjacent_pixels = calc_adjacent(pending_pixel, image, True)
                pending_pixels.extend(zip(adjacent_pixels, [pending_steps+1]*8))

                visited_steps[pending_pixel] = pending_steps
                for adjacent_pixel in adjacent_pixels:
                    visited_parents.setdefault(adjacent_pixel, pending_pixel)

        start_pixel = component[0]
        end_pixels = calc_adjacent(start_pixel, image, True)
        end_pixel = next(iter(sorted(end_pixels, reverse=True, key=lambda s: (
            visited_steps.get(s, -float('inf')),
            len([ap for ap in calc_adjacent(s, image, False) if is_empty(ap, image)]),
        ))), start_pixel)

        curr_pixel = end_pixel
        while curr_pixel:
            boundaries.append(curr_pixel)
            curr_pixel = visited_parents.get(curr_pixel, None)

        return boundaries

    silhouette_components = calc_components(silhouette_image)
    silhouette_boundaries = [calc_boundaries(silhouette_components[0], silhouette_image)]
    # silhouette_boundaries = [calc_boundaries(sc, silhouette_image) for sc in silhouette_components]

    color_list = [
        (255, 0, 0, 255), (255, 127, 0, 255), (255, 255, 0, 255),
        (0, 255, 0, 255), (0, 0, 255, 255), (75, 0, 130, 255),
        (148, 0, 211, 255)]

    for boundary_idx, boundary in enumerate(silhouette_boundaries):
        boundary_color = color_list[min(boundary_idx, len(color_list)-1)]
        for boundary_pixel in boundary:
            base_image.putpixel(boundary_pixel, boundary_color)

    '''
    for component_idx, component in enumerate(silhouette_components):
        component_color = color_list[min(component_idx, len(color_list)-1)]
        for component_pixel in component:
            base_image.putpixel(component_pixel, component_color)
    '''

    base_image.save(os.path.join(output_dir, 'test.png'))

### Miscellaneous ###

if __name__ == '__main__':
    main()
