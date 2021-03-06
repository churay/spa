__doc__ = '''Module for the Movie Class Implementation'''

import os, sys, math, shutil, inspect
import spa, ffmpeg

### Module Classes ###

class movie(object):
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

    def render(self, file_path, data_path=None, fps=60,
            encoding=ffmpeg.encoding.mp4, quality=0):
        ll = spa.level_logger('movie.render')

        ll.log('Creating Data Paths', 1)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        data_path = data_path or os.path.join(spa.output_dir, file_name)
        if not (spa.touch(file_path, is_dir=False, force=True) and
                spa.touch(data_path, is_dir=True, force=True)):
            return False

        # NOTE(JRC): For the sake of robustness, a movie is simply rendered
        # as a single frame sequence of the canvas if no sequences are given.
        if not self._sequences:
            self.add_sequence(lambda pf, **k: [self._canvas.copy()], 0.1)

        # NOTE(JRC): Processing one sequence type per loop allows the sequences
        # to be processed before the transitions.
        ll.log('Generating Sequences', 1)
        seq_frame_lists = [[] for s in self._sequences]
        for iter_seq_type in range(1, 3):
            iter_seq_str = 'Sequence' if iter_seq_type == 1 else 'Transition'
            ll.log('Processing %ss' % iter_seq_str, 2)
            for seq_index, (seq_func, seq_duration) in enumerate(self._sequences):
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
                    ll.log('Producing Frames for Sequence #%d' % (seq_index + 1), 3)
                    seq_args = tuple(adj_frames)[:iter_seq_type]
                    seq_kwargs = {'num_frames': int(math.ceil(fps * seq_duration))}
                    seq_frame_lists[seq_index].extend(seq_func(*seq_args, **seq_kwargs))

        ll.log('Applying Filters', 1)
        for seq_index, (seq_frames, seq_filters) in enumerate(zip(seq_frame_lists, self._filters)):
            for filt_index, (filt_func, window) in enumerate(seq_filters):
                ll.log('Filtering Sequence #%d w/ Filter #%d' % (seq_index, filt_index), 2)
                frame_window = tuple(int(m*len(seq_frames)) for m in window)
                filt_frames = seq_frames[frame_window[0]:frame_window[1]]
                new_frames = filt_func(filt_frames)

        '''
        # TODO(JRC): Fix a bug in this code that causes sequences with singular
        # frames to be deleted when adjacent to sequences with duplicates.
        ll.log('Smoothing Sequence Seams', 1)
        for prev_frames, curr_frames in zip(seq_frame_lists, seq_frame_lists[1:]):
            if prev_frames[-1].tobytes() == curr_frames[0].tobytes():
                prev_frames.pop()
        '''

        ll.log('Rendering Movie', 1)

        ll.log('Rendering Sequences', 2)
        seq_paths = []
        for seq_index, (_, duration) in enumerate(self._sequences):
            ll.log('Rendering Sequence #%d' % (seq_index + 1), 3)
            seq_path = os.path.join(data_path, '{0}-{1}.mp4'.format(file_name, seq_index))
            seq_tmpl = os.path.join(data_path, '{0}-{1}-%d.png'.format(file_name, seq_index))
            seq_fps = len(seq_frame_lists[seq_index]) / float(duration)

            for frame_index, frame in enumerate(seq_frame_lists[seq_index]):
                frame.save(os.path.join(data_path, seq_tmpl % frame_index))

            ffmpeg.render(seq_path, seq_tmpl, fps=seq_fps, quality=quality)
            seq_paths.append(seq_path)

        movie_path = os.path.join(data_path, '{0}.mp4'.format(file_name))
        temp_path = os.path.join(data_path, '.{0}.mp4'.format(file_name))

        ll.log('Concatenating Sequences', 2)
        shutil.copy2(seq_paths[0], movie_path)
        for seq_index, seq_path in enumerate(seq_paths[1:]):
            ll.log('Conatenating Sequence #%d' % (seq_index + 2), 3)
            ffmpeg.concat(temp_path, movie_path, seq_path, quality=quality)
            shutil.copy2(temp_path, movie_path)
        shutil.copy2(movie_path, file_path)

        ll.log('Encoding Sequence', 2)
        ffmpeg.encode(file_path, encoding, fps=fps, quality=quality)

        return True

    ### Helpers ###

    def _get_seq_type(self, index):
        sequence = self._sequences[index][0]
        return len(inspect.getargspec(sequence).args)
