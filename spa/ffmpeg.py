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

### Module Constants ###

encoding = type('Enum', (), {'mp4': 0, 'gif': 1})

### Module Functions ###

def ffmpeg(path, args, quality=0):
    '''NOTE(JRC): This is a raw FFMPEG call function. This function should
    only be used for internal one-off invocations.'''
    ffmpeg_args = ['ffmpeg']

    ffmpeg_args.extend(args)
    ffmpeg_args.extend(['-r', '60', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-y'])
    ffmpeg_args.extend(['-crf', '0' if quality == 1 else '22'])
    ffmpeg_args.append(path)

    # spa.log.debug(' '.join(ffmpeg_args))
    subprocess.check_output(ffmpeg_args, stderr=subprocess.STDOUT)

def encode(path, out_encoding, fps=60.0, quality=0):
    if out_encoding == encoding.gif:
        # NOTE(JRC): THe code below was adapted from the SO answer here:
        # https://askubuntu.com/a/648604/285545
        filter_flags = 'fps={0}'.format(fps)

        path_dir, path_base = os.path.dirname(path), os.path.basename(path)
        temp_path = os.path.join(path_dir, '.{0}'.format(path_base))
        palette_path = os.path.join(path_dir,
            '.{0}.png'.format(os.path.splitext(path_base)[0]))

        os.rename(path, temp_path)

        encode_args = ['ffmpeg']
        encode_args.extend(['-i', temp_path])
        encode_args.extend(['-r', '50', '-f', 'image2pipe', '-vcodec', 'ppm'])
        encode_args.extend(['-', '|'])
        encode_args.extend(['convert', '-delay', '2', '-loop', '0', '-', path])

        # spa.log.debug(' '.join(encode_args))
        subprocess.check_output(' '.join(encode_args), stderr=subprocess.STDOUT, shell=True)

        # TODO(JRC): Debug and re-enable the code below since it doesn't
        # require the use of the 'convert' utility.
        '''
        # NOTE(JRC): The code below was adapted from the tutorial here:
        # http://blog.pkh.me/p/21-high-quality-gif-with-ffmpeg.html
        ffmpeg_args = ['ffmpeg']
        ffmpeg_args.extend(['-i', temp_path])
        ffmpeg_args.extend(['-r', '60', '-framerate', str(fps)])
        ffmpeg_args.extend(['-vf', '{0},palettegen'.format(filter_flags), '-y'])
        ffmpeg_args.append(palette_path)

        # spa.log.debug(' '.join(ffmpeg_args))
        subprocess.check_output(ffmpeg_args, stderr=subprocess.STDOUT)

        ffmpeg_args = ['ffmpeg']
        ffmpeg_args.extend(['-i', temp_path, '-i', palette_path])
        ffmpeg_args.extend(['-r', '60', '-framerate', str(fps)])
        ffmpeg_args.extend(['-lavfi', '{0}[x];[x][1:v]paletteuse'.format(filter_flags), '-y'])
        ffmpeg_args.append(path)

        # spa.log.debug(' '.join(ffmpeg_args))
        subprocess.check_output(ffmpeg_args, stderr=subprocess.STDOUT)
        '''

        # TODO(JRC): Adapt this code so that these files are cleaned up
        # even if there are errors during processing above.
        # os.remove(palette_path)
        os.remove(temp_path)

def render(path, template, fps=60.0, quality=0):
    render_args = [
        '-framerate', str(fps),
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
