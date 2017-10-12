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

    '''
    movie = spa.movie()
    => specify the first frame somehow (canvas frame or canvas spec)

    a movie is a series of sequences (e.g. 'sstroke', 'scale')
    that are optionally connected by transitions (e.g. fade)
    with an arbitrary number of overlayed filters (e.g. 'overlay')

    (note: transitions are a special form of sequences)

    sequence: f(start_frame, ...) => [image]
    transition: f(start_frame, end_frame, ...) => [image]
    filter: f([frame], ...) => [image] (can also modify the images in place)

    movie.add_sequence(seq_func, duration, *args, index=-1, **kwargs)
    => when processed, this sequence will use the last frame of the previous sequence

    movie.add_transition(txn_func, duration, *args, index=-1, **kwargs)
    => when processed, this sequence will use the last frame of the previous and the first of the next

    movie.add_filter(filter_func, duration, *args, index=-1, window=(x, y), **kwargs)
    => when processed, this filter will be applied in replacing a piece of the sequence at the index in the given frame window

    spa.fx.sstroke(stroke_color=None, stroke_serial=False):

    movie = spa.movie(Image.new('RGBA', base_image.size, color=spa.color('white')))
    movie.add_sequence(spa.fx.sstroke, , base_image, )

    specify each sequence and how they're connected to form a pipeline
    then apply filters on top of subsequences

    movie.save('movie_name')
    => this function will save out multiple movie files (one for each sequence)
       and then stitch them together as a post-processing step (ffmpeg concat)
    '''

    '''
    movie = spa.movie(out_image)
    movie.add_sequence(lambda pf: spa.fx.sstroke(pf, base_image, spa.color('black'), stroke_serial=False), 1.0)
    # i need to be able to specify "use the last frame for this"
    movie.add_sequence(lambda pf: spa.fx.scale(pf, (point of scale), ), 1.0)
    '''

    movie_frames = []
    movie_frames.extend(spa.fx.sstroke(out_image, base_image, stroke_color=spa.color('black'), stroke_serial=True))
    movie_frames.extend(spa.fx.still(movie_frames[-1], frame_count=60))

    assert spa.render_movie('test', movie_frames, fps=60), 'Failed to render movie.'

### Miscellaneous ###

if __name__ == '__main__':
    main()
