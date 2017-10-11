__doc__ = '''Module for the Image Effects Functionality'''

import spa, imp

### Module Functions ###

# TODO(JRC): Write the implementation for all of these functions.
# - How will time frame be accounted for here?
# - How will cases where a subset of the image needs to be selected
#   be handled? (pass in a bbox perhaps?)

# TODO(JRC): Add support for stencils
def sstroke(in_image, out_image, serial=False):
    in_cells = imp.calc_opaque_cells(in_image)
    in_bounds = imp.calc_cell_boundaries(in_image, in_cells)
    in_strokes = imp.calc_cell_strokes(in_image, in_bounds)

    out_frames = [out_image.copy()]
    # TODO(JRC): Create a means of specifying an ordering for the serial
    # method of silhouette stroking.
    if serial:
        for in_stroke in [bs for bsl in in_strokes for bs in bsl]:
            for stroke_pixel in in_stroke:
                out_frame = out_frames[-1].copy()
                stroke_pixel_2d = imp.to_2d(stroke_pixel, in_image)
                out_frame.putpixel(stroke_pixel_2d, in_image.getpixel(stroke_pixel_2d)[:3])
                out_frames.append(out_frame)
    else:
        in_strokes = [isl for isls in in_strokes for isl in isls]
        num_frames = max(len(isl) for isl in in_strokes)

        # TODO(JRC): Refactor this piece a bit to make it more efficient
        # (eliminte the need for disposing so many lists by using something
        # like a number list that indicates how many boundaries need to filled
        # on the current frame).
        in_fills = []
        for in_stroke in in_strokes:
            stroke_fill = [[] for i in range(num_frames)]

            stroke_step = num_frames / float(len(in_stroke) - 1)
            stroke_offsets = [stroke_step * si for si in range(len(in_stroke))]
            for stroke_index, stroke_offset in enumerate(stroke_offsets):
                adj_stroke_offset = min(int(stroke_offset), num_frames - 1)
                stroke_fill[adj_stroke_offset].append(stroke_index)

            in_fills.append(stroke_fill)

        for frame_index in range(num_frames):
            frame_image = out_frames[-1].copy()
            for in_stroke, in_fill in zip(in_strokes, in_fills):
                for stroke_index in in_fill[frame_index]:
                    stroke_pixel_2d = imp.to_2d(in_stroke[stroke_index], in_image)
                    frame_image.putpixel(stroke_pixel_2d, in_image.getpixel(stroke_pixel_2d)[:3])
            out_frames.append(frame_image)

    return out_frames

def scale(in_image, out_image, scale_func):
    pass

def pop(out_image):
    pass

def hang(out_image, duration):
    return [out_image.copy() for i in range(duration)]
