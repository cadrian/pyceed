#!/usr/bin/env python3

import feedparser
from feed import atom
from feed.date.rfc3339 import tf_from_timestamp

xmldoc, out_feed = atom.new_xmldoc_feed()

d = feedparser.parse('http://www.courantpositif.fr/feed/')
print("~~ %s ~~" % d.feed.title)
out_feed.title = d.feed.title

for e in d.entries:
	print(" * [%s] %s" % (e.published, e.title))
	out_entry = atom.Entry()
	out_entry.title = e.title
	out_entry.published = tf_from_timestamp(e.published)
	out_entry.id = e.id
	out_feed.entries.append(out_entry)

print("\n\n%s" % xmldoc)
