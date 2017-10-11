__doc__ = '''Module for SPA ((Sequential Picture Amalgamator)) Globals'''

import os, sys, shutil, subprocess, json

### Module Constants ###

base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
input_dir = os.path.join(base_dir, 'in')
output_dir = os.path.join(base_dir, 'out')

colors = {
    'red':        (255,   0,   0),
    'green':      (  0, 255,   0),
    'blue':       (  0,   0, 255),

    'magenta':    (255,   0, 255),

    'black':      (  0,   0,   0),
    'white':      (255, 255, 255),
}

### Module Functions ###

def color(name, opacity=255):
    color_tuple = colors.get(name, 'black')
    return (color_tuple[0], color_tuple[1], color_tuple[2], opacity)

def display_status(item, curr, total):
    sys.stdout.write('\r')
    sys.stdout.write('  processing %s %d/%d...' % (item, curr+1, total))
    if curr + 1 >= total: sys.stdout.write('\n')
    sys.stdout.flush()

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

# TODO(JRC): Write a function that colorizes cache files so that they're
# easier to debug.
def cache(cache_id):
    def cache_decorator(func):
        def cache_func(image, *args):
            image_filename = os.path.basename(image.filename)
            image_name = os.path.splitext(image_filename)[0]
            cache_path = os.path.join(output_dir,
                '{0}_{1}.json'.format(image_name, cache_id))

            # If the cache file exists and has been modified more recently
            # than the source image file, then use the cached result.
            if os.path.isfile(cache_path) and \
                    os.path.getmtime(image.filename) < os.path.getmtime(cache_path):
                with open(cache_path, 'r') as cache_file:
                    result = json.load(cache_file)
                return result
            else:
                result = func(image, *args)
                with open(cache_path, 'w') as cache_file:
                    json.dump(result, cache_file)
                return result

        return cache_func
    return cache_decorator
