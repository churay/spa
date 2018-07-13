__doc__ = '''Empty Render Example'''

canvas_image = PIL.Image.new('RGBA', (100, 100), color=spa.colorize('white'))
movie = spa.movie(canvas_image)
