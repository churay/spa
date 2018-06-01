__doc__ = '''Module for the Image Effects Functionality'''

import os, random, collections
import spa, imp
from vector import vector
from PIL import Image

### Module Functions ###

def sstroke(canvas_image, cell_image,
        stroke_image=None,
        stroke_offset=vector(2, spa.align.mid),
        stencil=None,
        stencil_rate=1,            # units: pixels / stencil imprint
        **kwargs):
    # NOTE(JRC): Any pixel in the stencil with the color magenta will inherit
    # the color from the source 'cell_image' during the embedding process.
    stencil_color = stencil if isinstance(stencil, tuple) else spa.color('magenta')
    stencil_image = stencil if isinstance(stencil, Image.Image) else \
        Image.new('RGBA', (1, 1), color=stencil_color)

    stroke_offset = imp.calc_alignment(stroke_offset, canvas_image, cell_image)
    to_canvas = lambda sp: imp.to_pixel(sp + stroke_offset)
    get_pixel = lambda sp: cell_image.getpixel(imp.to_pixel(sp))[:3]

    stroke_cells = imp.calc_opaque_cells(cell_image)
    stroke_bounds = imp.calc_cell_boundaries(cell_image, stroke_cells)
    strokes = imp.calc_cell_strokes(cell_image, stroke_bounds)
    stroke_to_cell = {id(sl): sli for sli, sls in enumerate(strokes) for sl in sls}

    # NOTE(JRC): Each item in the 'ordered_strokes' list is a list that
    # enumerates a set of strokes that can performed concurrently.
    strokes = [sl for sls in strokes for sl in sls]
    if stroke_image:
        # NOTE(JRC): The 'stroke_to_cell' dictionary doesn't need to be updated
        # after these calls since the associated functions don't change the
        # memory addresses of any of the base lists that they're given.
        oriented_strokes = imp.orient_cell_strokes(cell_image, stroke_image, strokes)
        ordered_strokes = imp.order_cell_strokes(cell_image, stroke_image, oriented_strokes)
    else:
        ordered_strokes = [strokes]

    frame_images = [canvas_image.copy()]
    for curr_strokes in ordered_strokes:
        num_frames = max(len(sl) for sl in curr_strokes)
        stroke_fills = [spa.distribute(len(s), num_frames) for s in curr_strokes]
        for frame_index in range(num_frames):
            frame_image = frame_images[-1].copy()
            for stroke, stroke_fill in zip(curr_strokes, stroke_fills):
                stroke_cell = stroke_cells[stroke_to_cell[id(stroke)]]
                for stroke_index in stroke_fill[frame_index]:
                    # NOTE(JRC): This has the potential to create weird artifacting
                    # if a stroke fills many on-rate in a single frame.
                    if stroke_index % stencil_rate != 0: continue
                    pixel_offset = imp.to_2d(stroke[stroke_index], cell_image, True)
                    pixel_tangent = imp.calc_tangent(stroke, stroke_index, cell_image)

                    pixel_stencil_image = stencil_image.rotate(
                        vector(2, 1.0, 0.0).angleto(pixel_tangent),
                        resample=Image.BILINEAR)

                    pixel_stencil_offset = pixel_offset - \
                        imp.calc_alignment(vector(2, spa.align.mid), pixel_stencil_image)
                    cell_stencil_image = cell_image.crop((
                        pixel_stencil_offset[0], pixel_stencil_offset[1],
                        pixel_stencil_image.width, pixel_stencil_image.height))

                    # NOTE(JRC): This code enforces stencil color/alpha rules:
                    # - If the stencil has color magenta at a pixel, then it
                    #   inherits the color from the cell image. Otherwise, it
                    #   uses its own color.
                    # - If the pixel is outside the current cell being colored,
                    #   then it is automatically zeroed out (prevents artifacts).
                    cell_color_data = cell_stencil_image.getdata()
                    pixel_stencil_data = []
                    for cell_index, cell_color in enumerate(cell_color_data):
                        index_stencil_offset = imp.to2d(cell_index,
                            cell_stencil_image, True)
                        index_pixel = index_stencil_offset - pixel_stencil_offset
                        stencil_rgb = pixel_stencil_image.getpixel(index_pixel)[:3]
                        index_pixel = imp.to_1d(index_pixel[0], index_pixel[1],
                            cell_stencil_image, False)

                        cell_rgb, cell_alpha = cell_color[:3], cell_color[3]
                        index_rgb = cell_rgb if stencil_rgb == spa.color('magenta') \
                            else stencil_rgb
                        index_alpha = cell_alpha if index_pixel in stroke_cell \
                            else 0

                        pixel_stencil_data.append(tuple(index_rgb + [index_alpha]))
                    pixel_stencil_image.putdata(pixel_stencil_data)

                    frame_image.paste(pixel_stencil_image, box=(pixel_stencil_offset[0], pixel_stencil_offset[1]))
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
        canvas_image.paste(frame_image, imp.to_pixel(frame_offset), frame_image)

        frame_images.append(canvas_image)

    return frame_images

def pop(canvas_image, pop_image,
        pop_offset=vector(2, spa.align.mid),
        pop_rate=10,              # units: number / contour
        pop_velocity=0.05,        # units: pop image % / timescale
        pop_rotation=90,          # units: degrees / timescale
        pop_scale=0.07,           # units: pop image %
        pop_stencil=None,
        pop_seed=None,
        **kwargs):
    ffx = _get_fxdata(**kwargs)

    pop_offset = imp.calc_alignment(pop_offset, canvas_image, pop_image)
    pop_stencil = pop_stencil or spa.read_image('default.png', spa.imtype.stencil)
    pop_rng = random.seed(pop_seed)

    pop_cells = imp.calc_opaque_cells(pop_image)
    pop_bounds = imp.calc_cell_boundaries(pop_image, pop_cells)
    pop_strokes = imp.calc_cell_strokes(pop_image, pop_bounds)
    pop_contours = [sorted(psl, key=lambda p: len(p))[-1] for psl in pop_strokes]

    # Scale Parameters to Fit Image #

    scale_baseline = min(*pop_image.size)

    stencil_scale = vector(2, pop_scale * scale_baseline)
    pop_stencil = pop_stencil.resize(imp.to_pixel(stencil_scale), resample=Image.LANCZOS)
    stencil_offset = imp.calc_alignment(vector(2, spa.align.mid), pop_stencil)

    pop_velocity *= scale_baseline

    # Generate Contour Particles #

    pop_particles = []
    for contour in pop_contours:
        contour_orient = imp.calc_orientation(contour, pop_image)
        contour_dir = 1 if contour_orient == spa.orient.ccw else -1
        contour_distrib = spa.distribute(
            int(pop_rate), len(contour), bucket_limit=1, is_cyclic=True)

        # TODO(JRC): Consider adding randomness to the following attributes:
        # - Start Angle
        # - Velocity Magnitude
        # - Velocity Vector
        # - Rotation Magnitude
        contour_particles = []
        for pixel_index, pixel_particles in enumerate(contour_distrib):
            if not pixel_particles: continue
            pixel_pos = imp.to_2d(contour[pixel_index], pop_image, True)
            pixel_angle = 0

            pixel_tangent = imp.calc_tangent(contour, pixel_index, pop_image)
            pixel_normal = pixel_tangent.irotate(contour_dir * 90)

            pixel_velocity = (pop_velocity / float(ffx.num_frames)) * pixel_normal
            pixel_rotation = (1.0 / float(ffx.num_frames)) * pop_rotation

            contour_particles.append([
                pixel_pos, pixel_angle,
                pixel_velocity, pixel_rotation])

        pop_particles.extend(contour_particles)

    # Simulate Particles for Duration #

    alpha_func = lambda fu: 0 + 4*fu - 4*fu**2
    to_canvas = lambda pp: imp.to_pixel((pp + pop_offset) - stencil_offset)

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
            frame_image.paste(particle_image, to_canvas(particle[0]), particle_image)

            particle[0] += particle[2]
            particle[1] += particle[3]

        frame_images.append(frame_image)

    return frame_images

def fade(in_image, out_image,
        fade_func=lambda fu: (1.0 - fu, fu),
        fade_color=None,
        **kwargs):
    ffx = _get_fxdata(**kwargs)

    # TODO(JRC): Improve the robustness of this function by automatically
    # scaling the larger image to fit the smaller image.
    assert in_image.size == out_image.size, 'Cannot fade between images of different dimensions.'

    if fade_color != None:
        fade_image = Image.new('RGBA', in_image.size, color=fade_color)

        in_num_frames = int(ffx.num_frames / 2.0)
        out_num_frames = ffx.num_frames - in_num_frames

        # TODO(JRC): Remove the duplicate frame that will almost inevitably be
        # generated between these two frame sequences.
        frame_images = []
        frame_images.extend(fade(in_image, fade_image,
            fade_func=fade_func, num_frames=in_num_frames))
        frame_images.extend(fade(fade_image, out_image,
            fade_func=fade_func, num_frames=out_num_frames))
    else:
        frame_images = []
        for frame_index in range(ffx.num_frames):
            frame_end_images = [i.copy() for i in [in_image, out_image]]
            frame_end_alphas = fade_func(frame_index / max(ffx.num_frames - 1.0, 1.0))

            for end_image, end_alpha in zip(frame_end_images, frame_end_alphas):
                alpha_data = end_image.getdata(band=3)
                alpha_image = Image.new('L', end_image.size)
                alpha_image.putdata([int(end_alpha * ia) for ia in alpha_data])
                end_image.putalpha(alpha_image)

            frame_image = Image.alpha_composite(*tuple(frame_end_images))
            frame_images.append(frame_image)

    return frame_images

def still(in_image, still_color=spa.color('white'), **kwargs):
    if not still_color:
        return [in_image.copy()]
    else:
        still_image = Image.new('RGBA', in_image.size, color=still_color)
        still_image.paste(in_image, mask=in_image)
        return [still_image]

### Helper Types ###

fxdata = collections.namedtuple('fxdata', ['num_frames'])

### Helper Functions ###

def _get_fxdata(**kwargs):
    fxargs = {'num_frames': 0}
    fxargs = {k: kwargs.get(k, 0) for k, v in fxargs.iteritems()}
    return fxdata(**fxargs)
