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

    silhouette_image = Image.open(os.path.join(input_dir, 'silhouette.png'))
    overlay_image = Image.open(os.path.join(input_dir, 'overlay.png'))

    # TODO(JRC): Scale this image based on the scaling factor that will
    # be used for the pop effect.
    base_image = Image.new('RGBA', silhouette_image.size, color=(255, 255, 255, 255))

    ## Identify Connected Components ##

    # TODO(JRC): Refactor the following section so that it's easier to read.
    # TODO(JRC): Add status statements like the 'dmtg' project to make the wait bearable.

    visited_pixels = {}
    pending_pixels = list(
        ((x, y), -1) for x in range(silhouette_image.width)
        for y in range(silhouette_image.height)
        if silhouette_image.getpixel((x, y))[3] != 0)

    component_lists = []
    while pending_pixels:
        pending_pixel, pending_comp = pending_pixels.pop()
        pending_alpha = silhouette_image.getpixel(pending_pixel)[3]

        if pending_alpha != 0 and pending_pixel not in visited_pixels:
            if pending_comp == -1:
                pending_comp = len(component_lists)
                component_lists.append([])

            component_list = component_lists[pending_comp]
            component_list.append(pending_pixel)
            visited_pixels[pending_pixel] = pending_comp

            px, py = pending_pixel
            pending_pixels.extend(((px+dx, py+dy), pending_comp) for dx in range(-1, 2) for dy in range(-1, 2))

    color_list = [
        (255, 0, 0, 255), (255, 127, 0, 255), (255, 255, 0, 255),
        (0, 255, 0, 255), (0, 0, 255, 255), (75, 0, 130, 255),
        (148, 0, 211, 255)]

    # TODO(JRC): Figure out a better way to combine these small pockets of
    # connected components with larger nearby components.
    #component_lists = [cl for cl in component_lists if len(cl) > 20]

    for component_idx, component_list in enumerate(component_lists):
        component_color = color_list[min(component_idx, len(color_list)-1)]
        for component_pixel in component_list:
            base_image.putpixel(component_pixel, component_color)

    base_image.save(os.path.join(output_dir, 'test.png'))

### Miscellaneous ###

if __name__ == '__main__':
    main()
