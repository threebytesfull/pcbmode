## PCBmodE

[![Build Status][travis-image]][travis-url] [![Coverage Status][coveralls-image]][coveralls-url]

PCBmodE is a printed circuit board design Python script that creates an SVG from [JSON](http://en.wikipedia.org/wiki/JSON) input files, and then creates [Gerber](http://en.wikipedia.org/wiki/Gerber_format) and Excellon files for manufacturing.

PCBmodE gives the designer the freedom to place any arbitrary shape on any layer, as it is natively vector-based. Much of the design is done in a text editor -- editing JSON -- with viewing and some editing -- routing mostly -- done with [Inkscape](http://inkscape.org).

### Requirements

You'll need:
* Python 3.3 or later
* [PyParsing](http://pyparsing.wikispaces.com/)
* [lxml](http://lxml.de/)
* [Inkscape](http://inkscape.org)

PCBmodE is developed and tested under Linux and Mac OS X, so it might or might not work under other OSs. (It'd be helpful to know success or failure of attempts!)

### Resources

[Documentation](http://pcbmode.readthedocs.org)

[travis-image]: https://travis-ci.org/threebytesfull/pcbmode.svg?branch=develop
[travis-url]: https://travis-ci.org/threebytesfull/pcbmode

[coveralls-image]: https://coveralls.io/repos/threebytesfull/pcbmode/badge.svg?branch=develop&service=github
[coveralls-url]: https://coveralls.io/github/threebytesfull/pcbmode?branch=develop

### The name

The 'mod' in PCBmodE has a double meaning. The first is short for 'modern' (in contrast to tired old EDA tools). The second is a play on the familiar 'modifications' or 'mods' done to imperfect PCBs. Call it 'PCB mode' or 'PCB mod E', whichever you prefer.

### License

PCBmodE versions 3.0 and above are licensed under the [MIT License](http://opensource.org/licenses/MIT). Previous versions were licensed under the Apache 2.0 License.
