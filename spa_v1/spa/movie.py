__doc__ = '''Module for the Movie Class Implementation'''

import os, sys, shutil, inspect
import spa, ffmpeg

### Module Classes ###

class movie():
    ### Constructors ###

    def __init__(self, canvas):
        self._sequences, self._filters = [], []
        self._canvas = canvas.copy()

    ### Methods ###

    def add_sequence(self, seq_func, duration, index=None):
        index = index if index is not None else len(self._sequences)
        self._sequences.insert(index, (seq_func, duration))
        self._filters.insert(index, [])

    # TODO(JRC): For the time being, a filter 'window' can only be specified
    # in terms of percentage through the sequence (e.g. (0.0, 1.0) for the
    # whole sequence); eventually, support for more options may be desirable.
    def add_filter(self, filt_func, window, index=-1, subindex=-1):
        self._filters[index].insert(subindex, (filt_func, window))

    def rem_sequence(self, index=-1):
        self._sequences.pop(index)
        self._filters.pop(index)

    def rem_filter(self, index=-1, subindex=-1):
        self._filters[index].pop(subindex)

    def render(self, movie_name):
        seq_frame_lists = [[] for s in self._sequences]

        # Process Sequences #

        # NOTE(JRC): Processing one sequence type per loop allows the sequences
        # to be processed before the transitions.
        for iter_seq_type in range(1, 3):
            for seq_index, (seq_func, _) in enumerate(self._sequences):
                adj_frames = []
                for adj_index in [seq_index+o for o in [-1, 1]]:
                    if not (0 <= adj_index < len(self._sequences)) or \
                            not seq_frame_lists[adj_index] or \
                            self._get_seq_type(adj_index) == 2:
                        adj_frame = self._canvas
                    else:
                        frame_index = -1 if adj_index < seq_index else 0
                        adj_frame = seq_frame_lists[adj_index][frame_index]
                    adj_frames.append(adj_frame)

                if self._get_seq_type(seq_index) == iter_seq_type:
                    seq_frame_lists[seq_index].extend(seq_func(*tuple(adj_frames)[:iter_seq_type]))

        # Apply Filters #

        for seq_frames, seq_filters in zip(seq_frame_lists, self._filters):
            for filt_func, window in seq_filters:
                frame_window = tuple(int(m*len(seq_frames)) for m in window)
                filt_frames = seq_frames[frame_window[0]:frame_window[1]]
                new_frames = filt_func(filt_frames)

        # Render Movie #

        # TODO(JRC): Handle the case in which this function is called without
        # any input sequences.

        movie_dir = os.path.join(spa.output_dir, movie_name)
        shutil.rmtree(movie_dir, True)
        os.makedirs(movie_dir)

        seq_paths = []
        for seq_index, (_, duration) in enumerate(self._sequences):
            seq_path = os.path.join(movie_dir, '{0}-{1}.mp4'.format(movie_name, seq_index))
            seq_tmpl = os.path.join(movie_dir, '{0}-{1}-%d.png'.format(movie_name, seq_index))
            seq_fps = len(seq_frame_lists[seq_index]) / float(duration)

            for frame_index, frame in enumerate(seq_frame_lists[seq_index]):
                frame.save(os.path.join(movie_dir, seq_tmpl % frame_index))

            seq_output = ffmpeg.render(seq_path, seq_tmpl, fps=seq_fps)
            if not seq_output: return False

            seq_paths.append(seq_path)

        movie_path = os.path.join(movie_dir, '{0}.mp4'.format(movie_name))
        temp_path = os.path.join(movie_dir, '.{0}.mp4'.format(movie_name))

        shutil.copy2(seq_paths[0], movie_path)
        for seq_path in seq_paths[1:]:
            seq_concat = ffmpeg.concat(temp_path, movie_path, seq_path)
            if not seq_concat: return False
            shutil.copy2(temp_path, movie_path)

        return True

    ### Helpers ###

    def _get_seq_type(self, index):
        sequence = self._sequences[index][0]
        return len(inspect.getargspec(sequence).args)
