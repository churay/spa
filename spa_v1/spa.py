#!/usr/bin/env python

__doc__ = '''Module for "SPA" Console Application'''

import os
import spa
from PIL import Image

### Main Entry Point ###

def main():
    base_image = Image.open(os.path.join(spa.input_dir, 'silhouette_small.png'))#'silhouette.png'))
    over_image = Image.open(os.path.join(spa.input_dir, 'overlay.png'))
    # TODO(JRC): Scale this image based on the scaling factor that will
    # be used for the pop effect.
    out_image = Image.new('RGBA', base_image.size, color=spa.color('white'))

    movie_frames = []
    movie_frames.extend(spa.fx.sstroke(base_image, out_image, serial=False))
    movie_frames.extend(spa.fx.hang(movie_frames[-1], 60))

    assert spa.render_movie('test', movie_frames, fps=120), 'Failed to render movie.'

### Miscellaneous ###

if __name__ == '__main__':
    main()
