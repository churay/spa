#!/usr/bin/env python

__doc__ = '''Module for "SPA" Console Application

=== REQUIRED ===

* Implement the 'fx.fade' transition function.
* Write all of the final scripts.

=== OPTIONAL ===

* Add an option to the 'fx.sstroke' function to use a stencil that defines
  the area of the stroke image that's filled at each step.
* Improve the robustness of the 'movie.render' function so that it doesn't
  fail if there are no input sequences.

'''

import os, math
import spa
from PIL import Image

### Main Entry Point ###

def main():
    base_image = spa.read_image('silhouette_small.png')#'test4.png')#'silhouette.png')
    pop_image = spa.read_image('blue_star.png', spa.imtype.stencil)
    out_image = Image.new('RGBA', base_image.size, color=spa.color('white'))
    # out_image = Image.new('RGBA', tuple(int(1.5*d) for d in base_image.size), color=spa.color('white'))

    movie = spa.movie(out_image)

    # Current Test #

    movie.add_sequence(lambda pf, **k: spa.fx.still(Image.alpha_composite(out_image, base_image), **k), 0.1)
    movie.add_sequence(lambda pf, **k: spa.fx.pop(pf, base_image, pop_rate=15, pop_scale=0.06, pop_stencil=pop_image, **k), 0.5)
    movie.add_sequence(lambda pf, **k: spa.fx.still(pf, **k), 0.1)

    # Mock Final #

    '''
    movie.add_sequence(lambda pf, **k: spa.fx.sstroke(pf, base_image, stroke_color=spa.color('black'), stroke_serial=False, **k), 2.0)
    # TODO(JRC): Refine the function used here to have a bit more "pop"!
    movie.add_sequence(lambda pf, **k: spa.fx.scale(pf, lambda fu: 1 - 0.38*math.sin(1.5*math.pi*fu), **k), 0.7)
    # TODO(JRC): Create the image that's the silhouette with the overlay at scale.
    movie.add_sequence(lambda pf, **k: spa.fx.pop(pf, **k), 0.5)
    movie.add_sequence(lambda pf, **k: spa.fx.still(pf, **k), 0.1)
    '''

    # Stroke Test #

    '''
    movie.add_sequence(lambda pf, **k: spa.fx.sstroke(pf, base_image, stroke_color=spa.color('black'), stroke_serial=False, **k), 3.0)
    movie.add_sequence(lambda pf, **k: spa.fx.still(pf, **k), 0.5)
    '''

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

    assert movie.render('test', fps=60, log=True), 'Failed to render movie.'

### Miscellaneous ###

if __name__ == '__main__':
    main()
