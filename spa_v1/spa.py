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

    # TODO(JRC): Fix the following bugs:
    # - The concatenation feature isn't working for some reason (differing FPS maybe?).
    # - Videos with frame rates lower than number of frames (e.g. extended frames) don't
    #   render properly in VLC for some reason; meta-data looks right, but the video
    #   doesn't play properly.
    movie = spa.movie(out_image)
    movie.add_sequence(lambda pf: spa.fx.sstroke(pf, base_image, stroke_color=spa.color('black'), stroke_serial=True), 3.0)
    movie.add_sequence(lambda pf: spa.fx.still(pf, frame_count=60), 3.0)
    assert movie.render('test'), 'Failed to render movie.'

    '''
    movie_frames = []
    movie_frames.extend(spa.fx.sstroke(out_image, base_image, stroke_color=spa.color('black'), stroke_serial=True))
    movie_frames.extend(spa.fx.still(movie_frames[-1], frame_count=60))

    assert spa.render_movie('test', movie_frames, fps=60), 'Failed to render movie.'
    '''

### Miscellaneous ###

if __name__ == '__main__':
    main()
