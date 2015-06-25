# Feed

from internals import DbObject

class FeedException(Exception):
    pass

class Feed(DbObject):
    def __init__(self, cursor, rowid=None, url=None, **kw):
        if rowid is None:
            if url is None:
                raise FeedException("url is needed")
        DbObject.__init__(self, cursor, rowid=rowid, columns=("url", "etag"), url=url, **kw)

class FeedEntry(DbObject):
    def __init__(self, cursor, rowid=None, feed=None, **kw):
        if rowid is None:
            if feed is None:
                raise FeedException("feed is needed")
        DbObject.__init__(self, cursor, rowid=rowid, columns=("author", "updated", "published", "summary", "content", "feedid"), feedid=feed.id if feed else None, **kw)
        self.__feed = feed

    def __getattr__(self, name):
        if name == "feed":
            return self.__feed
        return super(FeedEntry, self).__getattr__(name)

    def __setattr__(self, name, value):
        if name == "feed":
            self.__feed = value)
            super(FeedEntry, self).__setattr__("feedid", value.id)
        else:
            super(FeedEntry, self).__setattr__(name, value)
