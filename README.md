# PyCeed #

PyCeed is a simple web-based feeds aggregator. It supports feeds union, pruning, sorting, and filtering. It contains a web server that serves simple config pages and feeds in both Atom and RSS formats.

IOW: a very trimmed-down *Yahoo! pipes* (which is about to close in a few months): no fancy operators, no pretty graphical configuration.

## Dependencies ##
* `python3` (tested with python 3.4)
* `python3-feedparser` >> 5.2 (not in debian, use github's latest) https://github.com/kurtmckee/feedparser
* `feedgen` 0.3.1 (not in debian, use pip) https://pypi.python.org/pypi/feedgen
* `bottle` 0.12 (tested with 0.12.8) http://bottlepy.org/
* `python3-apsw` (tested with 3.8.6-r1)
* `SQLite` 3.8 (tested with 3.8.7.1)
