__doc__ = '''"spa.fx.sstroke" Example'''

base_image = spa.load('test3_cells.png', spa.imtype.test)
stroke_image = spa.load('test3_strokes.png', spa.imtype.test)
out_image = PIL.Image.new('RGBA', base_image.size, color=spa.color('white'))

movie = spa.movie(out_image)
movie.add_sequence(lambda pf, **k: spa.fx.sstroke(pf, base_image,
    stroke_image=stroke_image, stroke_color=spa.color('black'), **k), 3.0)
movie.add_sequence(lambda pf, **k: spa.fx.still(pf, **k), 0.1)
