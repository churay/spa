#!/usr/bin/env python

__doc__ = '''Module for "SPA" Console Application'''

import os, sys
import spa
from PIL import Image

### Main Entry Point ###

def main():
    # TODO(JRC): Change 'spa.imp.find_best_stroke' above into an iterative
    # method so that this isn't necessary.
    sys.setrecursionlimit(5000)

    base_image = Image.open(os.path.join(spa.input_dir, 'silhouette_small.png'))#'silhouette.png'))
    over_image = Image.open(os.path.join(spa.input_dir, 'overlay.png'))

    # TODO(JRC): This is the full loading functionality, which only needs to
    # be re-run when there are changes to the base image.
    base_cells = spa.imp.calc_opaque_cells(base_image)
    base_boundaries = spa.imp.calc_cell_boundaries(base_image, base_cells)
    base_strokes = spa.imp.calc_cell_strokes(base_image, base_boundaries)
    base_colors = spa.imp.distrib_colors(len(base_cells))

    # TODO(JRC): Scale this image based on the scaling factor that will
    # be used for the pop effect.
    out_image = Image.new('RGBA', base_image.size, color=(255, 255, 255, 255))

    # TODO(JRC): When stroking the boundaries for all of the silhouettes, use
    # graph distance instead of pixel distance for the fill to prevent artifacting
    # on some silhouettes (e.g. the e).
    out_frames = [out_image.copy()]
    base_stroke_list = [bs for bsl in base_strokes for bs in bsl]
    num_stroke_frames = max(len(bsl) for bsl in base_stroke_list)

    base_stroke_fills = []
    for base_stroke in base_stroke_list:
        stroke_fill = [[] for i in range(num_stroke_frames)]

        stroke_step = num_stroke_frames / float(len(base_stroke) - 1)
        stroke_offsets = [stroke_step * si for si in range(len(base_stroke))]
        for stroke_index, stroke_offset in enumerate(stroke_offsets):
            adj_stroke_offset = min(int(stroke_offset), num_stroke_frames - 1)
            stroke_fill[adj_stroke_offset].append(stroke_index)

        base_stroke_fills.append(stroke_fill)

    for frame_index in range(num_stroke_frames):
        frame_image = out_frames[-1].copy()
        for base_stroke, base_fill in zip(base_stroke_list, base_stroke_fills):
            for stroke_index in base_fill[frame_index]:
                stroke_pixel = base_stroke[stroke_index]
                frame_image.putpixel(spa.imp.to_2d(stroke_pixel, out_image), (0, 0, 0, 255))
        out_frames.append(frame_image)

    '''
    for base_stroke in [bs for bsl in base_strokes for bs in bsl]:
        for stroke_pixel in base_stroke:
            out_frame = out_frames[-1].copy()
            out_frame.putpixel(spa.imp.to_2d(stroke_pixel, out_image), (0, 0, 0, 255))
            out_frames.append(out_frame)
    '''

    # TODO(JRC): Add a procedure that pads out the ending of a particular frame
    # sequence by a certain amount.
    out_frames += [out_frames[-1].copy() for i in range(60)]
    assert spa.render_movie('test', out_frames, fps=120), 'Failed to render movie.'

    '''
    for cell, color in zip(base_cells, base_colors):
        for cell_pixel in cell:
            out_image.putpixel(spa.imp.to_2d(cell_pixel, out_image), color)
    out_image.save(os.path.join(spa.output_dir, 'test.png'))
    '''

    '''
    for boundary_list, color in zip(base_boundaries, base_colors):
        for boundary in boundary_list:
            for boundary_pixel in boundary:
                out_image.putpixel(to_2d(boundary_pixel, out_image), color)
    out_image.save(os.path.join(spa.output_dir, 'test.png'))
    '''

### Miscellaneous ###

if __name__ == '__main__':
    main()
