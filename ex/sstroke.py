import spa
from PIL import Image

base_image = spa.read_image('test1_cells.png', spa.imtype.test)
stroke_image = spa.read_image('test1_strokes.png', spa.imtype.test)
out_image = Image.new('RGBA', base_image.size, color=spa.color('black'))

movie = spa.movie(out_image)
movie.add_sequence(lambda pf, **k: spa.fx.sstroke(pf, base_image,
    stroke_image=stroke_image, stroke_color=spa.color('white'), **k), 3.0)
