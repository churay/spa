__doc__ = '''"spa.fx.fade" Example'''

base_image = spa.load('test4.png', spa.imtype.test)
out_image = PIL.Image.new('RGBA', base_image.size, color=spa.color('white'))

movie = spa.movie(out_image)
movie.add_sequence(lambda pf, **k: spa.fx.still(base_image, **k), 0.1)
movie.add_sequence(lambda pf, nf, **k: spa.fx.fade(pf, nf,
    fade_color=spa.color('white'), **k), 2.0)
movie.add_sequence(lambda pf, **k: spa.fx.still(base_image, **k), 0.1)
