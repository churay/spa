# FFMPEG Information Document #

This document contains information related to the `ffmpeg` tool and how its
command-line options are used to generate the sequences output by this library.
The full documentation for the latest version of `ffmpeg` can be found [here][ffmpeg],
and the information that follows is the subset of the documentation that's
relevant to the procedures implemented in this code.

## `spa.fx.encode` Commands ##

The `spa.fx.encode` command was written using tips for rendering high-quality GIFs
found on [Ubitux's blog](http://blog.pkh.me/p/21-high-quality-gif-with-ffmpeg.html).
This process leverages two runs of `ffmpeg` to produce a result: the first run to
generate a GIF palette (which helps reduce dithering) and the second to GIF-ify
the MP4 source movie (which is the native output of `spa.fx.ffmpeg`). To explain
each of these commands, a basic template for each will be provided alongside an
overview of `ffmpeg`'s interpretation and usage of every flag/parameter.

### Palette Generation ###

The `ffmpeg` call for the palette generation step looks like the following:

```
ffmpeg -i (MP4 Source) -filter:v palettegen -y (Palette Output)
```

Here's what each flag represents:

- `-i (MP4 Source)`: An input stream for the encoding, which is just the source
- stream from which the GIF palette will be generated in this case.
- `-filter:v palettegen`: The filter specifier for the command, which indicates
  that this is a video-only filter that will apply the `palettegen` filter to
  generate a GIF palette. This is a simple transform (i.e. one with one input
  and one output), so the simple filter command is used here (i.e. `-filter`);
  for more complicated transformations, `-filter_complex` must be used instead
  (see below).
- `-y`: A flag that indicates that the command should automatically replace
  output files if they already exist.

### GIF Encoding ###

The `ffmpeg` call for the GIF encoding step is a bit more complicated and looks
like the following:

```
ffmpeg -i (MP4 Source) -i (Palette Source) -filter_complex fps=(oFPS)[x];[x][1:v]paletteuse -y (GIF Output)
```

Here's what each flag represents:

- `-i (MP4 Source) -i (Palette Source)`: Just as before, this is an input stream specifier,
  except this time there are multiple input streams. Each input stream is implicitly
  labeled with an index based on the order of its appearance in the argument list
  (in this example, the MP4 source is 0 and the palette source is 1).
- `-filter_complex fps=(oFPS)[x];[x][1:v]paletteuse`: The filter specifier for the
  command, which outlines the set of filters to be used in generating the output.
  Since this filter contains more than one input/output, the filter specifier must
  be given explicitly as a [filter graph][ffmpeg-fgraph]. In this filter graph,
  there are two filter chains: an FPS filter chain and a palette use filter chain.
  The first chain (i.e. `fps=(oFPS)[x]`) indicates that the [`fps`][ffmpeg-fps]
  filter will be applied to the MP4 source sequence (this is implied since the
  MP4 source is the first input and `fps` is the first chain in the graph) to
  generate a new stream to output pad `[x]`. The second chain (i.e. `[x][1:v]paletteuse`)
  specifies that the [`paletteuse`][ffmpeg-palette] filter will be applied using `[x]`
  as the source video (i.e. the re-scaled FPS sequence) and `[1:v]` as the source
  palette (i.e. the video channel of the second input parameter, which is the
  palette source) to produce an implied result. The result ends up being the GIF
  sequence since this is the last video output to the filter graph.
- `-y`: A flag that indicates that the command should automatically replace
  output files if they already exist.

[ffmpeg]: https://ffmpeg.org/ffmpeg-all.html
[ffmpeg-fgraph]: https://www.ffmpeg.org/ffmpeg-all.html#Filtergraph-description
[ffmpeg-fps]: https://www.ffmpeg.org/ffmpeg-all.html#fps-1
[ffmpeg-palette]: https://www.ffmpeg.org/ffmpeg-all.html#paletteuse
