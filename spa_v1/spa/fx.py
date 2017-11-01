__doc__ = '''Module for the Image Effects Functionality'''

import os, random, collections
import spa, imp
from vector import vector
from PIL import Image

### Module Functions ###

# TODO(JRC): Add support for stencils.
def sstroke(canvas_image, stroke_image,
        stroke_serial=False,
        stroke_offset=vector(2, spa.align.mid),
        stroke_color=None,
        **kwargs):
    stroke_offset = imp.calc_alignment(stroke_offset, canvas_image, stroke_image)
    to_canvas = lambda sp: (sp + stroke_offset).icoerce(int).dvals
    get_pixel = lambda sp: stroke_image.getpixel(sp.dvals)[:3]

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
                pixel_vec = imp.to_2d(stroke_pixel, stroke_image, True)
                pixel_color = stroke_color or get_pixel(pixel_vec)
                frame_image.putpixel(to_canvas(pixel_vec), pixel_color)
                frame_images.append(frame_image)
    else:
        num_frames = max(len(sl) for sl in strokes)
        stroke_fills = [spa.distribute(len(s), num_frames) for s in strokes]
        for frame_index in range(num_frames):
            frame_image = frame_images[-1].copy()
            for stroke, stroke_fill in zip(strokes, stroke_fills):
                for stroke_index in stroke_fill[frame_index]:
                    pixel_vec = imp.to_2d(stroke[stroke_index], stroke_image, True)
                    pixel_color = stroke_color or get_pixel(pixel_vec)
                    frame_image.putpixel(to_canvas(pixel_vec), pixel_color)
            frame_images.append(frame_image)

    return frame_images

def scale(scale_image, scale_func,
        scale_origin=vector(2, spa.align.mid),
        fill_color=spa.color('white'),
        **kwargs):
    ffx = _get_fxdata(**kwargs)

    scale_canvas = Image.new('RGBA', scale_image.size, color=fill_color)

    frame_images = []
    for frame_index in range(ffx.num_frames):
        canvas_image = scale_canvas.copy()

        frame_scale = scale_func(frame_index / max(ffx.num_frames - 1.0, 1.0))
        frame_scale_2d = tuple(int(frame_scale*d) for d in canvas_image.size)

        frame_image = scale_image.resize(frame_scale_2d, resample=Image.LANCZOS)
        frame_offset = imp.calc_alignment(scale_origin, canvas_image, frame_image)
        canvas_image.paste(frame_image, frame_offset.dvals)

        frame_images.append(canvas_image)

    return frame_images

def pop(canvas_image, pop_image,
        pop_offset=vector(2, spa.align.mid),
        pop_per_pixel=0.2,        # units: unit / pixel
        pop_velocity=0.1,         # units: screen % / timeframe
        pop_rotation=360,         # units: degrees / timeframe
        pop_stencil=None,
        pop_seed=None,
        **kwargs):
    ffx = _get_fxdata(**kwargs)

    pop_offset = imp.calc_alignment(pop_offset, canvas_image, pop_image)
    pop_stencil = pop_stencil or \
        Image.open(os.path.join(spa.input_dir, 'stencil_default.png'))
    pop_rng = random.seed(pop_seed)

    pop_cells = imp.calc_opaque_cells(pop_image)
    pop_bounds = imp.calc_cell_boundaries(pop_image, pop_cells)
    pop_strokes = imp.calc_cell_strokes(pop_image, pop_bounds)
    pop_contours = [sorted(psl, key=lambda p: len(p))[-1] for psl in pop_strokes]

    # Scale Stencil to Fit Contours #

    contour_min_bbox = sorted(
        [imp.calc_connected_bbox(pop_image, c) for c in pop_contours],
        key=lambda bb: bb[2]*bb[3])[0]
    contour_min_dim = min(contour_min_bbox)

    stencil_scale_2d = tuple(int(0.2*contour_min_dim) for d in range(2))
    pop_stencil = pop_stencil.resize(stencil_scale_2d, resample=Image.LANCZOS)
    stencil_offset = imp.calc_alignment(vector(2, spa.align.mid), pop_stencil)

    # Generate Contour Particles #

    pop_particles = []
    for contour in pop_contours:
        contour_orient = imp.calc_orientation(contour, pop_image)
        contour_dir = 1 if contour_orient == spa.orient.ccw else -1
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
            pixel_tangent = imp.calc_tangent(contour, pixel_index, pop_image)
            pixel_normal = pixel_tangent.irotate(contour_dir * 90)
            pixel_rotation = 2

            contour_particles.append([
                imp.to_2d(contour[pixel_index], pop_image, True), pixel_angle,
                pixel_normal, pixel_rotation])

        pop_particles.extend(contour_particles)

    # Simulate Particles for Duration #

    # TODO(JRC): Simulate the particles for the given number of frames
    # -> fade in and out during this whole process (fading interpolation function is some easing function)
    # -> apply and velocity to each particle
    # -> create the pop frame by stamping all of the stencils into the proper locations on the canvas.
    alpha_func = lambda fu: 0 + 4*fu - 4*fu**2
    to_canvas = lambda pp: ((pp + pop_offset) - stencil_offset).icoerce(int).dvals

    frame_images = []
    for frame_index in range(ffx.num_frames):
        frame_image = canvas_image.copy()
        stencil_image = pop_stencil.copy()

        particle_alpha = alpha_func(frame_index / max(ffx.num_frames - 1.0, 1.0))
        # TODO(JRC): Figure out a better workflow for modifying the alpha values
        # of the original image in batch.
        alpha_data = stencil_image.getdata(band=3)
        alpha_image = Image.new('L', stencil_image.size)
        alpha_image.putdata([int(particle_alpha*a) for a in alpha_data])
        stencil_image.putalpha(alpha_image)

        for particle in pop_particles:
            particle_image = stencil_image.rotate(particle[1], resample=Image.BILINEAR)
            frame_image.paste(particle_image, to_canvas(particle[0]))

            particle[0] += particle[2]
            particle[1] += particle[3]

        frame_images.append(frame_image)

    return frame_images

def crossfade(start_image, end_image, fade_color=None, **kwargs):
    # TODO(JRC): If a fade color is specified, then this is a full fade.
    # Otherwise, this is a cross-fade.
    # TODO(JRC): Allow specification of function for fade? (e.g. f(t)=>(s_a, e_a))
    ffx = _get_fxdata(**kwargs)
    pass

def still(image, **kwargs):
    return [image.copy()]

### Helper Types ###

fxdata = collections.namedtuple('fxdata', ['num_frames'])

### Helper Functions ###

def _get_fxdata(**kwargs):
    fxargs = {'num_frames': 0}
    fxargs = {k: kwargs.get(k, 0) for k, v in fxargs.iteritems()}
    return fxdata(**fxargs)
