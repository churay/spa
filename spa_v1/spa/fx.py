__doc__ = '''Module for the Image Effects Functionality'''

import spa, imp

### Module Functions ###

# TODO(JRC): Add support for stencils.
def sstroke(canvas_image, stroke_image, stroke_serial=False,
        stroke_offset=(spa.align.mid, spa.align.mid), stroke_color=None):
    stroke_offset = imp.calc_alignment(stroke_offset, canvas_image, stroke_image)
    to_canvas = lambda sp: tuple(d+dd for d, dd in zip(sp, stroke_offset))

    stroke_cells = imp.calc_opaque_cells(stroke_image)
    stroke_bounds = imp.calc_cell_boundaries(stroke_image, stroke_cells)
    strokes = imp.calc_cell_strokes(stroke_image, stroke_bounds)
    strokes = [sl for sls in strokes for sl in sls]

    frame_images = [canvas_image.copy()]
    # TODO(JRC): Create a means of specifying an ordering for the serial
    # method of silhouette stroking.
    if stroke_serial:
        for stroke in strokes:
            for stroke_pixel in stroke:
                frame_image = frame_images[-1].copy()
                pixel_2d = imp.to_2d(stroke_pixel, stroke_image)
                pixel_color = stroke_color or stroke_image.getpixel(pixel_2d)[:3]
                frame_image.putpixel(to_canvas(pixel_2d), pixel_color)
                frame_images.append(frame_image)
    else:
        num_frames = max(len(sl) for sl in strokes)

        # TODO(JRC): Refactor this piece a bit to make it more efficient
        # (eliminte the need for disposing so many lists by using something
        # like a number list that indicates how many boundaries need to filled
        # on the current frame).
        stroke_fills = []
        for stroke in strokes:
            stroke_fill = [[] for i in range(num_frames)]

            stroke_step = num_frames / float(len(stroke) - 1)
            stroke_offsets = [stroke_step * si for si in range(len(stroke))]
            for stroke_index, stroke_offset in enumerate(stroke_offsets):
                adj_stroke_offset = min(int(stroke_offset), num_frames - 1)
                stroke_fill[adj_stroke_offset].append(stroke_index)

            stroke_fills.append(stroke_fill)

        for frame_index in range(num_frames):
            frame_image = frame_images[-1].copy()
            for stroke, stroke_fill in zip(strokes, stroke_fills):
                for stroke_index in stroke_fill[frame_index]:
                    pixel_2d = imp.to_2d(stroke[stroke_index], stroke_image)
                    pixel_color = stroke_color or stroke_image.getpixel(pixel_2d)[:3]
                    frame_image.putpixel(to_canvas(pixel_2d), pixel_color)
            frame_images.append(frame_image)

    return frame_images

def scale(canvas_image, scale_func,
        scale_origin=(spa.align.mid, spa.align.mid), fill_color=None):
    pass

def pop(out_image):
    pass

def still(image, frame_count=1):
    return [image.copy() for i in range(frame_count)]
