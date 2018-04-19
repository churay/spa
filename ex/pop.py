import spa
from PIL import Image

base_image = spa.load('test4.png', spa.imtype.test)
pop_image = spa.load('blue_star.png', spa.imtype.stencil)
out_image = Image.new('RGBA', base_image.size, color=spa.color('white'))

movie = spa.movie(out_image)
movie.add_sequence(lambda pf, **k: spa.fx.still(base_image, **k), 0.1)
movie.add_sequence(lambda pf, **k: spa.fx.pop(pf, base_image, pop_stencil=pop_image,
    pop_rate=15, pop_scale=0.03, pop_velocity=0.1, **k), 0.5)
movie.add_sequence(lambda pf, **k: spa.fx.still(pf, **k), 0.1)
