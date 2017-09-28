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

    silhouette_image = Image.open(os.path.join(input_dir, 'test.png')) #'silhouette.png'))
    #overlay_image = Image.open(os.path.join(input_dir, 'overlay.png'))

    # TODO(JRC): Scale this image based on the scaling factor that will
    # be used for the pop effect.
    base_image = Image.new('RGBA', silhouette_image.size, color=(255, 255, 255, 255))

    ## Identify Connected Components ##

    # TODO(JRC): Add caching for the component data so that the turnaround
    # time for generating the full animation is improved.

    # TODO(JRC): Add bounds checking to this function relative to the image
    # size to prevent searching out of bounds.
    def calc_adjacent(pixel):
        px, py = pixel
        return [(px+dx, py+dy) for dx in range(-1, 2) for dy in range(-1, 2)]

    visited_pixels = {}
    pending_pixels = list(
        ((x, y), -1) for x in range(silhouette_image.width)
        for y in range(silhouette_image.height)
        if silhouette_image.getpixel((x, y))[3] != 0)

    components = []
    while pending_pixels:
        pending_pixel, pending_comp = pending_pixels.pop()
        pending_alpha = silhouette_image.getpixel(pending_pixel)[3]

        if pending_alpha != 0 and pending_pixel not in visited_pixels:
            if pending_comp == -1:
                pending_comp = len(components)
                components.append([])

            component = components[pending_comp]
            component.append(pending_pixel)
            visited_pixels[pending_pixel] = pending_comp

            adjacent_pixels = calc_adjacent(pending_pixel)
            pending_pixels.extend(zip(adjacent_pixels, [pending_comp]*9))

    # TODO(JRC): Identify the boundary pixels in each of the components;
    # each component will have a maximum of two boundaries.

    import pdb; pdb.set_trace()

    boundaries = [[]] * len(components)
    for component, boundary in zip(components, boundaries):
        # TODO(JRC): Throw away pixels that aren't directly on the boundary and
        # discontinue paths that are taking longer than the current number of steps
        # at a particular location.
        # TODO(JRC): We're currently only locating the outer boundary and ignoring
        # the inner (important for the o and the n).
        visited_steps, visited_parents = {}, {}
        pending_pixels = [(component[0], 0)]

        while pending_pixels:
            pending_pixel, pending_steps = pending_pixels.pop()
            adjacent_pixels = calc_adjacent(pending_pixel)

            # NOTE(JRC): This 'is_boundary' condition can be loosened to be some
            # level interior relative to the boundary to facilitate less jagged
            # boundary curves.
            is_boundary = any(silhouette_image.getpixel(ap)[3] == 0 for ap in adjacent_pixels)
            is_component = silhouette_image.getpixel(pending_pixel)[3] != 0
            if is_component and is_boundary and pending_steps < visited_steps.get(pending_pixel, float('inf')):
                visited_steps[pending_pixel] = pending_steps
                (visited_parents[ap] = pending_pixel for ap in adjacent_pixels)
                pending_pixels.extend(zip(adjacent_pixels, [pending_steps+1]*9))

        

        # TODO(JRC): Add all of the pixels 
        pass

    color_list = [
        (255, 0, 0, 255), (255, 127, 0, 255), (255, 255, 0, 255),
        (0, 255, 0, 255), (0, 0, 255, 255), (75, 0, 130, 255),
        (148, 0, 211, 255)]

    for boundary_idx, boundary in enumerate(boundaries):
        boundary_color = color_list[min(boundary_idx, len(color_list)-1)]
        for boundary_pixel in boundary:
            base_image.putpixel(boundary_pixel, boundary_color)

    '''
    for component_idx, component in enumerate(components):
        component_color = color_list[min(component_idx, len(color_list)-1)]
        for component_pixel in component:
            base_image.putpixel(component_pixel, component_color)
    '''

    base_image.save(os.path.join(output_dir, 'test.png'))

### Miscellaneous ###

if __name__ == '__main__':
    main()
