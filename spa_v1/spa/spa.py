__doc__ = '''Module for SPA ((Sequential Picture Amalgamator)) Globals'''

import os, sys, time, json, subprocess

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

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

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

def log(func):
    log_stack = []
    def do_log(text, level=1):
        def print_top_log(is_start=False, is_end=False):
            level = len(log_stack) - 1
            level_text, level_combo, level_start = log_stack[-1]
            if is_end: log_stack.pop()

            level_pad = '  ' * level
            level_title = ('%s' if is_start else '(%s)') % level_text
            level_timing = ' {%.2es}' % (time.clock() - level_start) if is_end else ''

            print '%s[%d.%s] %s%s' % (level_pad, level, level_combo, level_title, level_timing)

        level = clamp(level, 0, len(log_stack) + 1)
        combo = log_stack[level][1] + 1 if level < len(log_stack) else 0
        if log_stack and level >= len(log_stack):
            print_top_log(is_start=True)
        else:
            for higher_index, higher_level in enumerate(range(level, len(log_stack))):
                print_top_log(is_start=(higher_index == 0), is_end=True)

        log_stack.append((text, combo, time.clock()))
    def skip_log(text, level=1):
        pass

    def log_decorator(*args, **kwargs):
        setattr(log_decorator, 'log', do_log if kwargs.pop('log', False) else skip_log)

        log_decorator.log('Log for "%s"' % func.__name__, 0)
        result = func(*args, **kwargs)
        log_decorator.log('End for %s' % func.__name__, 0)

        return result

    return log_decorator
