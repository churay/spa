__doc__ = '''Module for FFMPEG Interface Functionality

For more information on the FFMPEG utlity and what its argument values mean,
please refer to the following documentation pages:

- Frame Rates: http://trac.ffmpeg.org/wiki/Slideshow#Framerates
- H264 Encoding Guide: https://trac.ffmpeg.org/wiki/Encode/H.264
- Input/Output Rates: https://stackoverflow.com/a/41797724/837221
- Combining Streams: http://www.bugcodemaster.com/article/concatenate-videos-using-ffmpeg
'''

import os, sys, subprocess
import spa

### Module Functions ###

def ffmpeg(path, args, quality=0):
    '''NOTE(JRC): This is a raw FFMPEG call function. This function should
    only be used for internal one-off invocations.'''
    ffmpeg_args = ['ffmpeg']

    ffmpeg_args.extend(args)
    ffmpeg_args.extend(['-r', 60, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-y'])

    ffmpeg_args.extend(['-crf', 0 if quality == 0 else 22])
    ffmpeg_args.extend(['-loglevel', '-8'])

    ffmpeg_args.append(path)

    ffmpeg_args = map(str, ffmpeg_args)
    subprocess.check_output(ffmpeg_args, stderr=subprocess.STDOUT)

def render(path, template, fps=60.0, quality=0):
    render_args = [
        '-framerate', fps,
        '-i', template,
    ]

    ffmpeg(path, render_args, quality=quality)

def concat(path, lhs_path, rhs_path, quality=0):
    concat_args = [
        '-i', lhs_path,
        '-i', rhs_path,
        '-filter_complex', '[0:v:0][1:v:0]concat=n=2:v=1[v]', '-map', '[v]',
    ]

    ffmpeg(path, concat_args, quality=quality)
