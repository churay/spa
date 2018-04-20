#!/usr/bin/env python

__doc__ = '''Module for "SPA" Console Application'''

import os, sys, math, argparse, logging, subprocess
import spa
from PIL import Image

### Main Entry Point ###

def main():
    # Argument Parsing #

    parser = argparse.ArgumentParser(description=
        'CLI for "S(equential)P(icture)A(malgamator)" Library')

    parser.add_argument('-f', '--fps', dest='fps', nargs='?',
        type=int,
        default=60,
        help='The framerate (in frames per second) of the output movie, '
        'which defaults to 60.')
    parser.add_argument('-q', '--quality', dest='quality', nargs='?',
        type=int,
        default=1,
        choices=[0, 1],
        help='The level of quality present in the result movie. This '
        'argument defaults to the highest available quality value.')

    # parser.add_argument('-e', '--encoding', dest='encoding', nargs='?',
    #     type=str,
    #     default='mp4',
    #     choices=['mp4', 'gif'],
    #     help='The type of encoding that will be used for the generated movie. '
    #     'The default encoding type is "mp4".')
    parser.add_argument('-o', '--output', dest='output', nargs='?',
        type=argparse.FileType('w+'),
        default=os.path.join(os.getcwd(), 'output.mp4'),
        help='The path to the output file for the generated movie. By default, '
        'this path will be set to be a file named "output.mp4" in the current '
        'working directory.')
    parser.add_argument('-d', '--outdir', dest='outdir', nargs='?',
        type=str,
        default='',
        help='The path to the output directory that contains all of the '
        'temporary/intermediate files generated for the movie. This argument '
        'is generally only specified when generating large movie files. '
        'By default, this value is set to "spa/output/(output_name)".')

    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
        default=False,
        help='If specified, this flag indicates that the script should '
        'generate verbose program output.')

    parser.add_argument('input',
        type=argparse.FileType('r'),
        help='The path to the input file used to generate this movie. This '
        'file should contain a Python script that produces a "spa.movie" '
        'object called "movie", which this script will use to generate the '
        'output.')

    # Argument Handling #

    spa_run = parser.parse_args()

    logging.basicConfig(format='%(message)s',
        level=logging.DEBUG if spa_run.verbose else logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.CRITICAL)

    spa_run.input.close()
    spa_run.input = os.path.realpath(spa_run.input.name)
    spa_run.output.close()
    spa_run.output = os.path.realpath(spa_run.output.name)

    # Script Behavior #

    try:
        input_vars = {
            '__file__': os.path.realpath(spa_run.input),
            'PIL': sys.modules['PIL'],
            'spa': sys.modules['spa'],
        }
        execfile(spa_run.input, input_vars)
    except Exception:
        spa.log.error(('Error in SPA execution file "{0}"; '
            'synopsis below.').format(spa_run.input))
        raise
    if 'movie' not in input_vars:
        raise ValueError(('Error in SPA execution file "{0}"; '
            'file fails to define a "movie" variable.').format(spa_run.input))
    if not isinstance(input_vars.get('movie', False), spa.movie):
        raise ValueError(('Error in SPA execution file "{0}"; '
            'file defines "movie" variable as non-"spa.movie" type.').format(spa_run.input))

    try:
        input_vars['movie'].render(
            spa_run.output, data_path=spa_run.outdir,
            fps=spa_run.fps, quality=spa_run.quality)
    except subprocess.CalledProcessError:
        spa.log.error(('Error processing SPA execution file "{0}"; '
            'the target movie failed to render with "ffmpeg"; '
            'synopsis below.').format(spa_run.input))
        raise
    except Exception:
        spa.log.error(('Error processing SPA execution file "{0}"; '
            'the "spa.movie.render" function encountered errors; '
            'synopsis below.').format(spa_run.input))
        raise

    return 0

### Miscellaneous ###

if __name__ == '__main__':
    sys.exit(main())
