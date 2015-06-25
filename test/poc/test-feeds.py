#!/usr/bin/env python3

import feedparser
from feedgen.feed import FeedGenerator

out_feed = FeedGenerator()

url = 'http://www.courantpositif.fr/feed/'
d = feedparser.parse(url)
print("~~ %s ~~" % d.feed.title)
out_feed.title(d.feed.title)
out_feed.subtitle(d.feed.subtitle)
out_feed.id(d.feed.get("id", "no id"))
out_feed.updated(d.feed.updated)

for e in d.entries:
    print(" * [%s] %s" % (e.published, e.title))
    out_entry = out_feed.add_entry()
    out_entry.title(e.title)
    out_entry.published(e.published)
    out_entry.updated(e.updated)
    out_entry.id(e.id)
    out_entry.summary(e.summary)
    for c in e.content:
        out_entry.content(content=c.value, type=c.type) #, src=c.base
    for l in e.links:
        print("   > [%s] %s" % (l.rel, l.href))
        out_entry.link(link=l)

print("\n\n%s" % out_feed.atom_str(pretty=True))
