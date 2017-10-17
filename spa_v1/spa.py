#!/usr/bin/env python

__doc__ = '''Module for "SPA" Console Application

TODO(JRC): The following list enumerates the big to-dos:

=== REQUIRED ===

* Add progress notifications w/ timings to make it easier to track the code
  and the effects that take the most time in the rendering step.
  * Add 'show_progress' flag or something similar to the 'movie.render' function.
* Add some form of flag or filter to make it possible to remove duplicate
  frames that occur in between sequences.
  * Desirable for the scaling transition in the intended final animation.
* Implement the 'fx.overlay' function.
* Implement the 'fx.pop' function.
* Implement the 'fx.fade' transition function.

=== OPTIONAL ===

* Add an option to the 'fx.sstroke' function to use a stencil that defines
  the area of the stroke image that's filled at each step.

'''

import os, math
import spa
from PIL import Image

### Main Entry Point ###

def main():
    base_image = Image.open(os.path.join(spa.input_dir, 'test2.png'))#'silhouette.png'))
    over_image = Image.open(os.path.join(spa.input_dir, 'overlay.png'))
    # TODO(JRC): Scale this image based on the scaling factor that will
    # be used for the pop effect.
    out_image = Image.new('RGBA', base_image.size, color=spa.color('white'))

    movie = spa.movie(out_image)

    # Current Test #

    movie.add_sequence(lambda pf: spa.fx.still(base_image), 0.1)
    movie.add_sequence(lambda pf: spa.fx.scale(pf, lambda fu: 1 - 2*fu + 2*fu**2, 60), 1.0)
    movie.add_sequence(lambda pf: spa.fx.scale(pf, lambda fu: 1 + 2*(0.5*fu) - 2*(0.5*fu)**2, 60), 1.0/2.0)
    movie.add_sequence(lambda pf: spa.fx.still(pf), 0.1)

    # Mock Final #

    '''
    movie.add_sequence(lambda pf: spa.fx.sstroke(pf, base_image, stroke_color=spa.color('black'), stroke_serial=False), 3.0)
    movie.add_sequence(lambda pf: spa.fx.scale(pf, lambda fu: 1 - 2*fu + 2*fu**2, 30), (1.0/2.5))
    movie.add_sequence(lambda pf: spa.fx.scale(pf, lambda fu: 1 + 2*(0.5*fu) - 2*(0.5*fu)**2, 30), (1.0/2.5)/2.0)
    movie.add_sequence(lambda pf: spa.fx.scale(pf, lambda fi: 1.0, 100), 3.0)
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

    assert movie.render('test', log=True), 'Failed to render movie.'

### Miscellaneous ###

if __name__ == '__main__':
    main()
