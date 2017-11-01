#!/usr/bin/env python

__doc__ = '''Module for "SPA" Console Application

=== REQUIRED ===

* Modify the 'pop' function to use velocity based on the duration and the
  dt between frames (i.e. make units per second instead of per frame).
  - frames per second and duration? that gives us the number of frames,
    and tells us how fast we need to go potentially
    - for the pop effect, we'd go some distance proportional to the length
      of the curve and the scale of the picture
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
    movie.add_sequence(lambda pf, **k: spa.fx.still(Image.alpha_composite(out_image, base_image), **k), 0.1)
    movie.add_sequence(lambda pf, **k: spa.fx.pop(, **k), 1.0)
    movie.add_sequence(lambda pf, **k: spa.fx.still(pf, **k), 0.1)
    '''

    # Mock Final #

    '''
    movie.add_sequence(lambda pf, **k: spa.fx.sstroke(pf, base_image, stroke_color=spa.color('black'), stroke_serial=False, **k), 2.0)
    # TODO(JRC): Refine the function used here to have a bit more "pop"!
    movie.add_sequence(lambda pf, **k: spa.fx.scale(pf, lambda fu: 1 - 0.38*math.sin(1.5*math.pi*fu), **k), 0.7)
    # TODO(JRC): Create the image that's the silhouette with the overlay at scale.
    movie.add_sequence(lambda pf, **k: spa.fx.pop(pf, **k), 0.5)
    movie.add_sequence(lambda pf, **k: spa.fx.still(pf, **k), 0.1)
    '''

    # Basic Test #

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

    movie.add_sequence(lambda pf, **k: spa.fx.still(base_image, **k), 0.1)
    movie.add_sequence(lambda pf, **k: spa.fx.pop(pf, pf, pop_per_pixel=0.05, **k), 1.0)
    movie.add_sequence(lambda pf, **k: spa.fx.still(pf, **k), 0.1)

    assert movie.render('test', fps=60, log=True), 'Failed to render movie.'

### Miscellaneous ###

if __name__ == '__main__':
    main()
