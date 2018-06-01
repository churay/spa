__doc__ = '''"spa.fx.sstroke" Example (Stencil)'''

base_image = spa.load('test4_cells.png', spa.imtype.test)
stencil_image = spa.load('test4_brush.png', spa.imtype.stencil)
out_image = PIL.Image.new('RGBA', base_image.size, color=spa.color('white'))

movie = spa.movie(out_image)
movie.add_sequence(lambda pf, **k: spa.fx.sstroke(pf, base_image,
    stencil=stencil_image, **k), 3.0)
movie.add_sequence(lambda pf, **k: spa.fx.still(pf, **k), 0.1)
