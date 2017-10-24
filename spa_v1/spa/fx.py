__doc__ = '''Module for the Image Effects Functionality'''

import random
import spa, imp
from PIL import Image

### Module Functions ###

# TODO(JRC): Add support for stencils.
def sstroke(canvas_image, stroke_image, stroke_serial=False,
        stroke_offset=(spa.align.mid, spa.align.mid), stroke_color=None):
    stroke_offset = imp.calc_alignment(stroke_offset, canvas_image, stroke_image)
    to_canvas = lambda sp: spa.vecop(sp, stroke_offset)

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

        stroke_fills = [spa.distribute(len(s), num_frames) for s in strokes]
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
def pop(pop_image, pop_contours, pop_per_pixel, pop_num_frames,
        pop_stencil=None, pop_seed=None):
    pop_rng = random.seed(pop_seed)

    # TODO(JRC): Scale the stencil appropriately based on the size of the source image.
    pass

    pop_particles = []
    for contour in pop_contours:
        contour_normal_rotation = tuple(
            1 if imp.calc_orientation(contour, pop_image) == spa.orient.ccw else -1
            for i in range(2))
        contour_distrib = spa.distribute(
            int(len(contour) * pop_per_pixel), len(contour), bucket_limit=1)

        contour_particles = []
        for pixel_index, pixel_particles in enumerate(contour_distrib):
            if not pixel_particles: continue

            pixel_tangent = spa.vecop(
                imp.to_2d(contour[pixel_index-2], pop_image),
                imp.to_2d(contour[pixel_index+2], pop_image),
                vecop=lambda l, r: l - r)
            pixel_normal = spa.vecop(
                (pixel_tangent[1], -pixel_tangent[0]),
                contour_normal_rotation,
                vecop=lambda l, r: l * r)

            # TODO(JRC): Generate the randomized velocity (small perturbation to
            # the normal) and the rotation (random rotation amount between ranges).

            contour_particles.append((contour[pixel_index], None, None))

        pop_particles.extend(contour_particles)

    # TODO(JRC): Simulate the particles for the given number of frames
    # -> fade in and out during this whole process (fading interpolation function is some easing function)
    # -> apply and velocity to each particle (?) using RNG to vary values
    # -> create the pop frame by stamping all of the stencils into the proper locations on the canvas.

def still(image, frame_count=1):
    return [image.copy() for i in range(frame_count)]
