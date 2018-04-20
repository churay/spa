__doc__ = '''"spa.fx.scale" Example'''

import math

base_image = spa.load('test2_cells.png', spa.imtype.test)
out_image = PIL.Image.new('RGBA', base_image.size, color=spa.color('white'))

movie = spa.movie(out_image)
movie.add_sequence(lambda pf, **k: spa.fx.still(base_image, **k), 0.1)
movie.add_sequence(lambda pf, **k: spa.fx.scale(pf, lambda fu: 1.0+0.5*math.cos(math.pi*(fu+0.5)), **k), 1.0)
movie.add_sequence(lambda pf, **k: spa.fx.still(pf, **k), 0.1)
