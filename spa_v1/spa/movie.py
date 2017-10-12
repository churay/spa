__doc__ = '''Module for the Movie Class Implementation'''

import collections

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

spa.fx.sstroke(stroke_color=None, serial=False):

movie = spa.movie(Image.new('RGBA', base_image.size, color=spa.color('white')))
movie.add_sequence(spa.fx.sstroke, , base_image, )

specify each sequence and how they're connected to form a pipeline
then apply filters on top of subsequences

movie.save('movie_name')
=> this function will save out multiple movie files (one for each sequence)
   and then stitch them together as a post-processing step (ffmpeg concat)
'''

### Module Classes ###

class movie():
    ### Constructors ###

    def __init__(self, canvas):
        self._sequences, self._filters = [], []
        self._canvas = canvas.copy()

    ### Methods ###

    def add_sequence(seq_func, duration, index=-1):
        pass

    def add_transition(tran_func, duration, index=-1):
        pass

    # TODO(JRC): Figure out what arguments need to be added here in order
    # to allow filters to be applied to a subset of a sequence.
    def add_filter(filt_func, index=-1, **kwargs):
        pass

    def save(name):
        pass

    ### Helpers ###

    # TODO(JRC): Remove this function once it's determined to be absolutely
    # unnecessary with a different scheme for sequence/filter specification.
    def _filter_args(in_args, in_kwargs, local_kwargs):
        func_args = in_args[:]
        func_kwargs = {k: v for k, v in in_kwargs.iteritems() if k not in local_kwargs}
        local_kwargs = {k: in_kwargs.get(k, v) for k, v in local_kwargs.iteritems()}

        return (func_args, func_kwargs, local_kwargs)
