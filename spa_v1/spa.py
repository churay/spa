#!/usr/bin/env python

__doc__ = '''Module for "SPA" Console Application

=== REQUIRED ===

* Implement the 'fx.pop' function.
* Implement the 'fx.fade' transition function.

=== OPTIONAL ===

* Add an option to the 'fx.sstroke' function to use a stencil that defines
  the area of the stroke image that's filled at each step.
* Modify the sequencing functions with frames to accept a time limit and a
  frame rate instead of a frame count.

'''

import os, math
import spa
from PIL import Image

### Main Entry Point ###

def main():
    base_image = Image.open(os.path.join(spa.input_dir, 'test4.png'))#'silhouette.png'))
    over_image = Image.open(os.path.join(spa.input_dir, 'overlay.png'))
    out_image = Image.new('RGBA', base_image.size, color=spa.color('white'))
    #out_image = Image.new('RGBA', tuple(int(1.5*d) for d in base_image.size), color=spa.color('white'))

    movie = spa.movie(out_image)

    # Current Test #

    '''
    movie.add_sequence(lambda pf: spa.fx.still(Image.alpha_composite(out_image, base_image)), 0.1)
    movie.add_sequence(lambda pf: spa.fx.pop(), 1.0)
    movie.add_sequence(lambda pf: spa.fx.still(pf), 0.1)
    '''

    # Mock Final #

    '''
    movie.add_sequence(lambda pf: spa.fx.sstroke(pf, base_image, stroke_color=spa.color('black'), stroke_serial=False), 2.0)
    # TODO(JRC): Refine the function used here to have a bit more "pop"!
    movie.add_sequence(lambda pf: spa.fx.scale(pf, lambda fu: 1 - 0.38*math.sin(1.5*math.pi*fu), 30), 0.7)
    # TODO(JRC): Create the image that's the silhouette with the overlay at scale.
    #movie.add_sequence(lambda pf: spa.fx.pop(pf, ...), 0.5)
    movie.add_sequence(lambda pf: spa.fx.still(pf), 0.1)
    '''

    # Basic Test #

    '''
    movie.add_sequence(lambda pf: spa.fx.sstroke(pf, base_image, stroke_color=spa.color('black'), stroke_serial=False), 3.0)
    movie.add_sequence(lambda pf: spa.fx.still(pf), 0.5)
    '''

    # Scale Test #

    '''
    movie.add_sequence(lambda pf: spa.fx.still(base_image), 0.1)
    movie.add_sequence(lambda pf: spa.fx.scale(pf, lambda fu: 1.0+0.5*math.cos(math.pi*(fu+0.5)), 60), 1.0)
    movie.add_sequence(lambda pf: spa.fx.still(pf), 0.1)
    '''

    # Pop Test #

    movie.add_sequence(lambda pf: spa.fx.still(base_image), 0.1)
    movie.add_sequence(lambda pf: spa.fx.pop(pf, pf, 30, pop_per_pixel=0.1), 0.5)
    movie.add_sequence(lambda pf: spa.fx.still(pf), 0.1)

    render_opts = {
        'log': True,
        'smooth_seams': True }
    assert movie.render('test', **render_opts), 'Failed to render movie.'

### Miscellaneous ###

if __name__ == '__main__':
    main()
