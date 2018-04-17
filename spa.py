#!/usr/bin/env python

__doc__ = '''Module for "SPA" Console Application'''

import os, math, argparse, logging
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
    # parser.add_argument('-q', '--quality', dest='quality', nargs='?',
    #     type=int,
    #     default=1,
    #     choices=[0, 1],
    #     help='The level of quality present in the result movie. This '
    #     'argument defaults to the highest available quality value.')

    # parser.add_argument('-e', '--encoding', dest='encoding', nargs='?',
    #     type=str,
    #     default='mp4',
    #     choices=['mp4', 'gif'],
    #     help='The type of encoding that will be used for the generated movie. '
    #     'The default encoding type is "mp4".')
    # parser.add_argument('-o', '--output', dest='output', nargs='?',
    #     type=argparse.FileType('w+'),
    #     default=os.path.join(os.getcwd(), 'output.mp4'),
    #     help='The path to the output file for the generated movie. By default, '
    #     'this path will be set to be a file named "output.mp4" in the current '
    #     'working directory.')
    # parser.add_argument('-d', '--outdir', dest='outdir', nargs='?',
    #     type=str,
    #     default='',
    #     help='The path to the output directory that contains all of the '
    #     'temporary/intermediate files generated for the movie. This argument '
    #     'is generally only specified when generating large movie files. '
    #     'By default, this value is set to "spa/output/(output_name)".')

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
        level=logging.INFO if spa_run.verbose else logging.WARNING)

    spa_run.input.close()
    spa_run.input = os.path.realpath(spa_run.input.name)
    # spa_run.output.close()
    # spa_run.output = os.path.realpath(spa_run.output.name)

    # spa_run.outdir = spa_run.outdir or \
    #     os.path.join(spa.output_dir, os.path.splitext(spa_run.output)[0])
    # if not os.path.exists(spa_run.outdir):
    #     os.makedirs(spa_run.outdir)


    # Script Behavior #

    input_valid = True
    try:
        input_vars = {}
        execfile(spa_run.input, input_vars)
    except Exception as e:
        logging.error(('Unable to execute input file "{0}"; '
            'error synopsis below.').format(spa_run.input))
        logging.error(str(e))
        input_valid = False

    if input_valid and 'movie' not in input_vars:
        logging.error(('Unable to generate movie from "{0}"; '
            'script fails to generated "movie" variable.').format(spa_run.input))
        input_valid = False

    if input_valid and not isinstance(input_vars.get('movie', False), spa.movie):
        logging.error(('Unable to generate movie from "{0}"; '
            'script "movie" variable is not a "spa.movie".').format(spa_run.input))
        input_valid = False

    movie_rendered = False
    if input_valid:
        movie = input_vars['movie']
        # movie_rendered = movie.render(spa_run.outdir, fps=spa_run.fps, log=spa_run.verbose)
        movie_rendered = movie.render(os.path.splitext(os.path.basename(spa_run.input))[0], fps=spa_run.fps, log=spa_run.verbose)
        if not movie_rendered:
            logging.error(('Unable to generate movie from "{}"; '
                'rendering process failed.').format(spa_run.input))

    return 0 if movie_rendered else 1

### Miscellaneous ###

if __name__ == '__main__':
    main()
