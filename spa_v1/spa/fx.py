__doc__ = '''Module for the Image Effects Functionality'''

import os, random
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
def pop(canvas_image, pop_image, pop_num_frames,
        pop_offset=(spa.align.mid, spa.align.mid),
        pop_per_pixel=1.0/5.0, pop_stencil=None, pop_seed=None):
    pop_offset = imp.calc_alignment(pop_offset, canvas_image, pop_image)
    to_canvas = lambda pp: spa.vecop(pp, pop_offset)

    pop_stencil = pop_stencil or \
        Image.open(os.path.join(spa.input_dir, 'stencil_default.png'))
    pop_rng = random.seed(pop_seed)

    pop_cells = imp.calc_opaque_cells(pop_image)
    pop_bounds = imp.calc_cell_boundaries(pop_image, pop_cells)
    pop_strokes = imp.calc_cell_strokes(pop_image, pop_bounds)
    pop_contours = [sorted(psl, key=lambda p: len(p))[-1] for psl in pop_strokes]

    # Scale Stencil to Fit Contours #

    stencil_bbox = (0, 0, pop_stencil.width, pop_stencil.height)
    contour_min_bbox = sorted(
        [imp.calc_connected_bbox(pop_image, c) for c in pop_contours],
        key=lambda bb: bb[2]*bb[3])[0]

    stencil_area = reduce(lambda a, n: a*n, stencil_bbox[2:], 1.0)
    contour_min_area = reduce(lambda a, n: a*n, contour_min_bbox[2:], 1.0)

    # stencil_target_frac = 0.05
    # stencil_curr_frac = stencil_area / contour_min_area

    # stencil_scale = stencil_target_frac / stencil_curr_frac
    # stencil_scale_2d = tuple(int(stencil_scale*d) for d in pop_stencil.size)
    stencil_scale_2d = tuple(int(0.05*d) for d in canvas_image.size)
    pop_stencil = pop_stencil.resize(stencil_scale_2d, resample=Image.LANCZOS)

    # Generate Contour Particles #

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

            pixel_angle = 0

            # TODO(JRC): Generate the randomized velocity (small perturbation to
            # the normal) and the rotation (random rotation amount between ranges).
            # NOTE(JRC): Both the velocity and the magnitude are per frame values.
            # There should probably be some consideration made toward really low
            # velocity values so that accumulations happen and jumps only occur
            # when the proper threshold is reached.
            pixel_tangent = spa.vecop(
                imp.to_2d(contour[(pixel_index-2)], pop_image),
                imp.to_2d(contour[(pixel_index+2)%len(contour)], pop_image),
                op=lambda l, r: l - r)
            pixel_normal = spa.vecop(
                (pixel_tangent[1], -pixel_tangent[0]),
                contour_normal_rotation,
                op=lambda l, r: l * r)
            pixel_rotation = 2

            contour_particles.append([
                imp.to_2d(contour[pixel_index], pop_image), pixel_angle,
                pixel_normal, pixel_rotation])

        pop_particles.extend(contour_particles)

    # Simulate Particles for Duration #

    # TODO(JRC): Simulate the particles for the given number of frames
    # -> fade in and out during this whole process (fading interpolation function is some easing function)
    # -> apply and velocity to each particle
    # -> create the pop frame by stamping all of the stencils into the proper locations on the canvas.
    alpha_func = lambda fu: 0 + 4*fu - 4*fu**2

    frame_images = []
    for frame_index in range(pop_num_frames):
        frame_image = canvas_image.copy()
        stencil_image = pop_stencil.copy()

        particle_alpha = alpha_func(frame_index / max(pop_num_frames - 1.0, 1.0))
        # TODO(JRC): Figure out a better workflow for modifying the alpha values
        # of the original image in batch.
        alpha_data = stencil_image.getdata(band=3)
        alpha_image = Image.new('L', stencil_image.size)
        alpha_image.putdata([int(particle_alpha*a) for a in alpha_data])
        stencil_image.putalpha(alpha_image)

        for particle in pop_particles:
            # particle_image = stencil_image.copy()
            # particle_image.rotate(particle[1], resample=Image.BILINEAR)

            particle_offset = spa.vecop(pop_offset, particle[0])
            frame_image.paste(stencil_image, particle_offset)

            particle[0] = spa.vecop(particle[0], particle[2])
            particle[1] += particle[3]

        frame_images.append(frame_image)

    return frame_images

def crossfade(start_image, end_image, fade_num_frames, fade_color=None):
    # TODO(JRC): If a fade color is specified, then this is a full fade.
    # Otherwise, this is a cross-fade.
    # TODO(JRC): Allow specification of function for fade? (e.g. f(t)=>(s_a, e_a))
    pass

def still(image, frame_count=1):
    return [image.copy() for i in range(frame_count)]
