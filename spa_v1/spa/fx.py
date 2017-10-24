__doc__ = '''Module for the Image Effects Functionality'''

import random
import spa, imp
from PIL import Image

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
            stroke_offs = [stroke_step * si for si in range(len(stroke))]
            for stroke_index, stroke_off in enumerate(stroke_offs):
                adj_stroke_offset = min(int(stroke_off), num_frames - 1)
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

def scale(scale_image, scale_func, scale_num_frames,
        scale_origin=(spa.align.mid, spa.align.mid),
        fill_color=spa.color('white')):
    scale_canvas = Image.new('RGBA', scale_image.size, color=fill_color)

    frame_images = []
    for frame_index in range(scale_num_frames):
        canvas_image = scale_canvas.copy()

        frame_scale = scale_func(frame_index / max(scale_num_frames - 1.0, 1.0))
        frame_scale_2d = tuple(int(frame_scale*d) for d in canvas_image.size)

        frame_image = scale_image.resize(frame_scale_2d, resample=Image.LANCZOS)
        frame_offset = imp.calc_alignment(scale_origin, canvas_image, frame_image)
        canvas_image.paste(frame_image, frame_offset)

        frame_images.append(canvas_image)

    return frame_images

# TODO(JRC): As the contours, pass the largest of each list (outermost contours
# of each cell) as a single-level list.
# TODO(JRC): Scale the stencil appropriately based on the size of the source image.
def pop(pop_image, pop_contours, pop_per_pixel, pop_num_frames,
        pop_stencil=None, pop_seed=None):
    # TODO(JRC): Determine which contours are cyclic and which are not.
    # TODO(JRC): Create the pop frame by stamping all of the stencils into
    # the proper locations on the canvas.
    pop_rng = random.seed(pop_seed)

    # TODO(JRC): Implement the algorithm outlined by the following pseudocode:
    # for each contour, figure out the contour metadata
    # -> open/closed contour?
    # -> direction of rotation for normal (based on open/closed, CW/CCW)
    #
    # generate all of the pop particles and their initial velocities (based on normal)
    # -> number of particles based on pop_per_pixel, calculate per boundary and then distribute randomly using rng
    # -> need 'imp.normal' function (calculate normal of contour)
    #
    # simulate the particles for the given number of frames
    # -> fade in and out during this whole process (fading interpolation function is some easing function)
    # -> apply torque and velocity to each particle (?) using RNG to vary values

    pass

    for pop_contour in pop_contours:
        pass

    pass

def still(image, frame_count=1):
    return [image.copy() for i in range(frame_count)]
