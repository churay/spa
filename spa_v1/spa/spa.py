__doc__ = '''Module for SPA ((Sequential Picture Amalgamator)) Globals'''

import os, sys, json, subprocess

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

align = type('Enum', (), {'lo': -3, 'mid': -2, 'hi': -1})

### Module Functions ###

def color(name, opacity=255):
    color_tuple = colors.get(name, 'black')
    return (color_tuple[0], color_tuple[1], color_tuple[2], opacity)

def display_status(item, curr, total):
    sys.stdout.write('\r')
    sys.stdout.write('  processing %s %d/%d...' % (item, curr+1, total))
    if curr + 1 >= total: sys.stdout.write('\n')
    sys.stdout.flush()

# TODO(JRC): Write a function that colorizes cache files so that they're
# easier to debug.
def cache(cache_id):
    def cache_decorator(func):
        def cache_func(image, *args, **kwargs):
            if not hasattr(image, 'filename'): return func(image, *args)

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
                result = func(image, *args, **kwargs)
                with open(cache_path, 'w') as cache_file:
                    json.dump(result, cache_file)
                return result

        return cache_func
    return cache_decorator

# TODO(JRC): Make this really cool where the number of seconds since the
# last log of the same level is reported.
def log(func):
    # TODO(JRC): Defer printing until the next thing is printed, or the function ends.
    # Print out timings at the end (when the next thing appears)
    # If we reach more than 1 down, then print the original call in quotations
    # log(0) => log(1) => log(2) => log(0)
    # log(0) => print out immediately
    log_stack = []
    def do_log(text, indent=0): print '%s%s' % ('  ' * (indent + 1), text)
    def skip_log(text, indent=0): pass

    def log_decorator(*args, **kwargs):
        setattr(log_decorator, 'log', do_log if kwargs.pop('log', False) else skip_log)
        getattr(log_decorator, 'log')('Log for "%s" [[' % func.__name__, -1)
        return func(*args, **kwargs)

    return log_decorator
