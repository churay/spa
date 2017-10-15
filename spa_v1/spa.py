#!/usr/bin/env python

__doc__ = '''Module for "SPA" Console Application'''

import os
import spa
from PIL import Image

### Main Entry Point ###

def main():
    base_image = Image.open(os.path.join(spa.input_dir, 'test3.png'))#'silhouette.png'))
    over_image = Image.open(os.path.join(spa.input_dir, 'overlay.png'))
    # TODO(JRC): Scale this image based on the scaling factor that will
    # be used for the pop effect.
    out_image = Image.new('RGBA', base_image.size, color=spa.color('white'))

    movie = spa.movie(out_image)
    movie.add_sequence(lambda pf: spa.fx.sstroke(pf, base_image, stroke_color=spa.color('black'), stroke_serial=True), 3.0)
    movie.add_sequence(lambda pf: spa.fx.still(pf), 0.5)
    assert movie.render('test'), 'Failed to render movie.'

### Miscellaneous ###

if __name__ == '__main__':
    main()
