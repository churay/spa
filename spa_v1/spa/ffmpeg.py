__doc__ = '''Module for FFMPEG Interface Functionality

For more information on the FFMPEG utlity and what its argument values mean,
please refer to the following documentation pages:

- Frame Rates: http://trac.ffmpeg.org/wiki/Slideshow#Framerates
- H264 Encoding Guide: https://trac.ffmpeg.org/wiki/Encode/H.264
- Input/Output Rates: https://stackoverflow.com/a/41797724/837221
- Combining Streams: http://www.bugcodemaster.com/article/concatenate-videos-using-ffmpeg
'''

import os, sys, subprocess

### Module Constants ###

debug = False
quality = True

### Module Functions ###

def ffmpeg(path, args):
    '''NOTE(JRC): This is a raw FFMPEG call function. This function should
    only be used for internal one-off invocations.'''
    ffmpeg_args = ['ffmpeg']

    ffmpeg_args.extend(args)
    ffmpeg_args.extend(['-r', 60, '-c:v', 'libx264', '-pix_fmt', 'yuv420p'])

    ffmpeg_args.extend(['-crf', 0 if quality else 22])
    ffmpeg_args.extend([] if debug else ['-loglevel', '-8'])

    ffmpeg_args.append(path)

    ffmpeg_call = ' '.join(map(str, ffmpeg_args))
    if debug: print ffmpeg_call
    return subprocess.call(ffmpeg_call, shell=True) == 0

def render(path, template, fps=60.0):
    render_args = [
        '-framerate', fps,
        '-i', template,
    ]

    return ffmpeg(path, render_args)

def concat(path, lhs_path, rhs_path):
    concat_args = [
        '-i', lhs_path,
        '-i', rhs_path,
        '-filter_complex', '[0:v:0][1:v:0]concat=n=2:v=1[v]', '-map', '[v]',
    ]

    return ffmpeg(path, concat_args)
