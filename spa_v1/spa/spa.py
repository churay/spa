__doc__ = '''Module for SPA ((Sequential Picture Amalgamator)) Globals'''

import os, sys, collections, time, json, subprocess

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
orient = type('Enum', (), {'none': 0, 'cw': 1, 'ccw': 2})

### Module Functions ###

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def distribute(num_items, num_buckets, bucket_limit=float('inf')):
    assert num_items <= num_buckets * bucket_limit, 'Not enough space for items.'

    buckets = [collections.deque() for b in range(num_buckets)]
    def add_to_bucket(item, bucket_index, fill_dir=None):
        fill_dir = fill_dir or (1 if bucket_index < num_buckets / 2 else -1)
        bucket = buckets[bucket_index]

        bucket.append(item)
        if len(bucket) > bucket_limit:
            evicted_item = bucket.popleft()
            adjacent_bucket_index = bucket_index + fill_dir
            add_to_bucket(evicted_item, adjacent_bucket_index, fill_dir=fill_dir)

    uniform_step = num_buckets / (num_items - 1.0)
    uniform_offsets = [uniform_step * si for si in range(num_items)]
    for item, offset in enumerate(uniform_offsets):
        bucket_index = min(int(offset), num_buckets - 1)
        add_to_bucket(item, bucket_index)

    # return [list(b) if bucket_limit != 1 else b.pop() for b in buckets]
    return [list(b) for b in buckets]

def color(name, opacity=255):
    color_tuple = colors.get(name, 'black')
    return (color_tuple[0], color_tuple[1], color_tuple[2], opacity)

def vecop(lhs, rhs, op=lambda l, r: l+r):
    return tuple(op(l, r) for l, r in zip(lhs, rhs))

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
