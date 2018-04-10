#!/usr/bin/env python

__doc__ = '''Module for "SPA" Console Application

=== REQUIRED ===

* Write all of the final scripts.

=== OPTIONAL ===

* Add an option to the 'fx.sstroke' function to use a stencil that defines
  the area of the stroke image that's filled at each step.
* Improve the robustness of the 'movie.render' function so that it doesn't
  fail if there are no input sequences.
* Improve quality of life for stroke function so that configuration doesn't
  affect the output image.
'''

import os, math
import spa
from PIL import Image

### Main Entry Point ###

def main():
    base_name = 'test1'
    base_image = spa.read_image('%s_cells.png' % base_name, spa.imtype.test)
    stroke_image = spa.read_image('%s_strokes.png' % base_name, spa.imtype.test)
    pop_image = spa.read_image('orange_star.png', spa.imtype.stencil)
    out_image = Image.new('RGBA', base_image.size, color=spa.color('white'))

    movie = spa.movie(out_image)

    # Current Test #

    '''
    movie.add_sequence(lambda pf, **k: spa.fx.sstroke(pf, base_image,
        stroke_image=stroke_image, stroke_serial=False,
        stroke_color=spa.color('black'), **k), 2.0)
    movie.add_sequence(lambda pf, **k: spa.fx.pop(base_image, base_image,
        pop_rate=10, pop_scale=0.05, pop_velocity=0.025, pop_rotation=270,
        pop_stencil=pop_image, **k), 0.5)
    movie.add_sequence(lambda pf, **k: spa.fx.still(pf, **k), 0.1)
    '''

    # Stroke Test #

    movie.add_sequence(lambda pf, **k: spa.fx.sstroke(pf, base_image,
        stroke_image=stroke_image, stroke_serial=False,
        stroke_color=spa.color('black'), **k), 3.0)
    movie.add_sequence(lambda pf, **k: spa.fx.still(pf, **k), 0.5)

    # Scale Test #

    '''
    movie.add_sequence(lambda pf, **k: spa.fx.still(base_image, **k), 0.1)
    movie.add_sequence(lambda pf, **k: spa.fx.scale(pf, lambda fu: 1.0+0.5*math.cos(math.pi*(fu+0.5)), **k), 1.0)
    movie.add_sequence(lambda pf, **k: spa.fx.still(pf, **k), 0.1)
    '''

    # Pop Test #

    '''
    movie.add_sequence(lambda pf, **k: spa.fx.still(base_image, **k), 0.1)
    movie.add_sequence(lambda pf, **k: spa.fx.pop(pf, pf, pop_rate=15, pop_scale=0.03, **k), 0.5)
    movie.add_sequence(lambda pf, **k: spa.fx.still(pf, **k), 0.1)
    '''

    # Fade Test #

    '''
    movie.add_sequence(lambda pf, **k: spa.fx.still(base_image, **k), 0.1)
    movie.add_sequence(lambda pf, nf, **k: spa.fx.fade(pf, nf, fade_color=spa.color('white'), **k), 2.0)
    movie.add_sequence(lambda pf, **k: spa.fx.still(base_image, **k), 0.1)
    '''

    # Mock Final #

    '''
    canvas_scale = 1.50
    embed_scale = 0.9 * canvas_scale
    canvas_color = spa.color('white')

    # TODO(JRC): Refine the functions used here to have a bit more "pop"!
    ease_in = lambda fu: 1.0 - (embed_scale - 1.0) * math.sin(1.5 * math.pi * fu)
    ease_out = lambda fu: 1.0 - (embed_scale - 1.0) * math.sin(1.5 * math.pi * fu)

    base_image = spa.read_image('logo_silh_small.png')
    pop_image = spa.read_image('blue_star.png', spa.imtype.stencil)

    canvas_image = Image.new('RGBA',
        spa.imp.to_pixel(canvas_scale * spa.vector(2, *base_image.size)),
        color=canvas_color)

    over_image = spa.read_image('logo_combo_small.png')
    over_image = over_image.resize(
        spa.imp.to_pixel(embed_scale * spa.vector(2, *base_image.size)),
        resample=Image.LANCZOS)

    over_frame = canvas_image.copy()
    over_offset = spa.imp.calc_alignment(spa.vector(2, spa.align.mid),
        canvas_image, over_image)
    over_frame.paste(over_image, spa.imp.to_pixel(over_offset), over_image)

    over_frame.save(os.path.join(spa.output_dir, 'over_test.png'))

    # TODO(JRC): Fix up issues with scaling the images and its interference
    # with the loops for the various component contours.
    movie = spa.movie(canvas_image)
    # movie.add_sequence(lambda pf, **k: spa.fx.sstroke(pf, base_image, stroke_serial=False, **k), 2.0)
    # movie.add_sequence(lambda pf, **k: spa.fx.scale(pf, ease_in, **k), 1.0)
    movie.add_sequence(lambda pf, **k: spa.fx.pop(over_frame, over_image, pop_rate=15, pop_scale=0.06, pop_stencil=pop_image, **k), 0.5)
    # movie.add_sequence(lambda pf, **k: spa.fx.scale(pf, ease_in, **k), 1.0)
    '''

    assert movie.render('test', fps=60, log=True), 'Failed to render movie.'

### Miscellaneous ###

if __name__ == '__main__':
    main()
