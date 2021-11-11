# `spa`: Sequential Picture Amalgamator #

`spa` is a Python CLI utility and library that generates simple animations
using a variety of image processing techniques. As a library, `spa` provides
image effect functions that can be used to produce MP4 and GIF animations
(via [ffmpeg][spa-ffmpeg]) from base [Pillow][spa-pillow] images. As a CLI
utility, `spa` intakes user-specified Python control files containing a
`movie = spa.movie(...)` variable and generates corresponding MP4/GIF files.

## Demos ##

### Scale Effect ###

![`spa` scale demo](https://github.com/churay/spa/raw/master/doc/gif/scale.gif)

```
(venv) $ ./spa.py -v -e gif -o scale.gif ex/scale.py
```

### Particle Pop Effect ###

![`spa` pop demo](https://github.com/churay/spa/raw/master/doc/gif/pop.gif)

```
(venv) $ ./spa.py -v -e gif -o pop.gif ex/pop.py
```

### Silhouette Stroke Effect ###

![`spa` sstroke demo](https://github.com/churay/spa/raw/master/doc/gif/sstroke.gif)

```
(venv) $ ./spa.py -v -e gif -o sstroke.gif ex/sstroke.py
```

## Install/Test Instructions ##

To build and run on Ubuntu 16.04+, execute the following commands:

```
# Install third-party dependencies.
$ sudo apt-get install ffmpeg pyton-pip python-virtualenv

# Create a virtual environment and install Python dependencies.
$ virtualenv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt

# Run one of the test cases to generate a test gif (see ex/ directory).
(venv) $ ./spa.py -v -e gif -o pop.gif ex/pop.py
```

### Dependencies ###

- [ffmpeg][spa-ffmpeg]
- [Python 2.7.X](https://www.python.org/)
- [Virtualenv](https://pypi.org/project/virtualenv/)
- [Pip](https://pypi.org/project/pip/)
- [Pillow][spa-pillow]

## License ##

This project is licensed under [the GPL v3 License][spa-license].


[spa-ffmpeg]: https://ffmpeg.org/
[spa-pillow]: https://pypi.org/project/Pillow/
[spa-gimp]: https://www.gimp.org/
[spa-gimp-el]: https://github.com/khalim19/gimp-plugin-export-layers
[spa-license]: https://raw.githubusercontent.com/churay/spa/master/liscense.txt
