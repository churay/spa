__doc__ = '''Module for SPA ((Sequential Picture Amalgamator)) Globals'''

import os, sys, shutil, logging, collections, time, json, subprocess
from PIL import Image

### Module Setup ###

log = logging.getLogger('spa')
log.addHandler(logging.NullHandler())

### Module Constants ###

base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
input_dir = os.path.join(base_dir, 'in')
output_dir = os.path.join(base_dir, 'out')
temp_dir = os.path.join(base_dir, 'tmp')
stencil_dir = os.path.join(input_dir, 'stencils')
test_dir = os.path.join(input_dir, 'tests')

colors = {
    'red':        (255,   0,   0),
    'green':      (  0, 255,   0),
    'blue':       (  0,   0, 255),
    'magenta':    (255,   0, 255),
    'black':      (  0,   0,   0),
    'white':      (255, 255, 255),
}

align = type('Enum', (), {'lo': -3, 'mid': -2, 'hi': -1})
orient = type('Enum', (), {e: i for i, e in
    enumerate(['none', 'cw', 'ccw'])})
imtype = type('Enum', (), {e: i for i, e in
    enumerate(['input', 'output', 'temp', 'stencil', 'test'])})

### Module Functions ###

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def colorize(name, alpha=255):
    color_tuple = colors.get(name, 'black')
    return color(color_tuple[0], color_tuple[1], color_tuple[2], alpha)

def distribute(num_items, num_buckets, bucket_limit=float('inf'), is_cyclic=False):
    # TODO(JRC): Add better support to allow overfilling to the front if the
    # requested distribution is cyclic.
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

    uniform_step = num_buckets / (num_items - (0.0 if is_cyclic else 1.0))
    uniform_offsets = [uniform_step * si for si in range(num_items)]
    for item, offset in enumerate(uniform_offsets):
        bucket_index = min(int(offset), num_buckets - 1)
        add_to_bucket(item, bucket_index)

    # return [list(b) if bucket_limit != 1 else b.pop() for b in buckets]
    return [list(b) for b in buckets]

def load(image_name, image_type=imtype.input):
    type_to_dir = {
        imtype.input: input_dir,
        imtype.output: output_dir,
        imtype.temp: temp_dir,
        imtype.stencil: stencil_dir,
        imtype.test: test_dir}

    return Image.open(os.path.join(type_to_dir[image_type], image_name))

def touch(path, is_dir=False, force=False):
    path_dir = os.path.realpath(path)
    if not is_dir: path_dir = os.path.dirname(path_dir)

    touch_succeeded = True
    if os.path.exists(path):
        if force:
            try:
                if os.path.isfile(path): os.remove(path)
                else: shutil.rmtree(path)
            except OSError as e:
                logging.warning(('Could not force removal of path at "{0}" due '
                    'to OS error; please check path permissions.').format(path))
                touch_succeeded = False
        elif not (os.path.isdir if is_dir else os.path.isfile)(path):
            logging.warning(('Touched path "{0}" exists, but is of '
                'wrong type "{1}".').format(path, 'dir' if is_dir else 'file'))
            touch_succeeded = False

    if not os.path.exists(path):
        try:
            if not os.path.exists(path_dir):
                os.makedirs(path_dir)
            if not is_dir:
                with open(path, "w+") as type_file: pass
        except OSError as e:
            logging.warning(('Could not touch path at "{0}" due to OS error; '
                'please check path permissions.').format(path))
            touch_succeeded = False

    return touch_succeeded

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
                touch(cache_path, is_dir=False, force=False)
                with open(cache_path, 'w') as cache_file:
                    json.dump(result, cache_file)
                return result

        return cache_func
    return cache_decorator

### Module Classes ###

class color(tuple):
    def __new__(self, r, g, b, a=255):
        return tuple.__new__(color, (r, g, b, a))

    def matches(self, other):
        other = other if isinstance(other, color) else colorize(other)
        return self.rgb == other.rgb

    def composite(self, other):
        other = other if isinstance(other, color) else colorize(other)
        return color(*[int(round(255.0*(sc/255.0)*(oc/255.0)))
            for sc, oc in zip(self, other)])

    @property
    def r(self):
        return self[0]
    @property
    def g(self):
        return self[1]
    @property
    def b(self):
        return self[2]
    @property
    def a(self):
        return self[3]

    @property
    def rgb(self):
        return self[:3]
    @property
    def rgba(self):
        return self[:4]

class level_logger(object):
    def __init__(self, context):
        self._context = context
        self._levels = []

        self.log('"{0}" Call'.format(self._context), 0)

    def __del__(self):
        self.log('"{0}" Call'.format(self._context), 0)

    def log(self, text, level):
        level = clamp(level, 0, len(self._levels) + 1)
        is_new_sublevel = level >= len(self._levels)

        sublevel = 0 if is_new_sublevel else self._levels[level][1] + 1
        if self._levels and is_new_sublevel:
            self._log(is_start=True)
        else:
            for higher_index, _ in enumerate(range(level, len(self._levels))):
                self._log(is_start=(higher_index == 0), is_end=True)

        self._levels.append((text, sublevel, time.clock()))

    def _log(self, is_start=False, is_end=False):
        level = len(self._levels) - 1
        level_text, level_sublevel, level_start = self._levels[-1]
        if is_end: self._levels.pop()

        level_pad = '  ' * level
        level_title = ('%s' if is_start else '(%s)') % level_text
        level_timing = ' {%.2es}' % (time.clock() - level_start) if is_end else ''

        log.info('%s[%d.%s] %s%s' % \
            (level_pad, level, level_sublevel, level_title, level_timing))
