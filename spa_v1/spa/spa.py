__doc__ = '''Module for SPA ((Sequential Picture Amalgamator)) Globals'''

import os, sys, shutil, subprocess

### Module Constants ###

base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
input_dir = os.path.join(base_dir, 'in')
output_dir = os.path.join(base_dir, 'out')

### Module Functions ###

def render_movie(movie_name, frames, fps=60):
    movie_dir = os.path.join(output_dir, movie_name)
    shutil.rmtree(movie_dir, True)
    os.makedirs(movie_dir)

    movie_path = os.path.join(movie_dir, '{0}.mp4'.format(movie_name))
    frame_tmpl = os.path.join(movie_dir, '{0}-%d.png'.format(movie_name))
    for frame_index, frame in enumerate(frames):
        frame.save(os.path.join(movie_dir, frame_tmpl % frame_index))

    movie_args = ['ffmpeg',
        '-r', fps,
        '-i', frame_tmpl,
        '-c:v', 'libx264',
        '-vb', '6000k',
        '-pix_fmt', 'yuv420p',
        #'-loglevel', '-8',
        movie_path]
    movie_err = subprocess.call(map(str, movie_args))

    return movie_err == 0

def display_status(item, curr, total):
    sys.stdout.write('\r')
    sys.stdout.write('  processing %s %d/%d...' % (item, curr+1, total))
    if curr + 1 >= total: sys.stdout.write('\n')
    sys.stdout.flush()
