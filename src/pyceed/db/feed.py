# Feed

from pyceed.db.internals import DbException, _DbObject


class FeedException(DbException):
    pass


class Feed(_DbObject):
    _columns = ("url", "etag")

    def __new__(cls, transaction, rowid=None, url=None, **data):
        if rowid is None:
            if url is None:
                raise FeedException("url is needed")
        data["url"] = url
        return super(Feed, cls).__new__(cls, transaction, rowid, **data)


class FeedEntry(_DbObject):
    _columns = ("author", "updated", "published", "summary", "content", "feedid")

    def __new__(cls, transaction, rowid=None, feed=None, feedid=None, **data):
        if rowid is None:
            if feed is None:
                if feedid is None:
                    raise FeedException("feed or feedid is needed")
                else:
                    feed = Feed(cursor=transaction, rowid=feedid)
            elif feedid is None:
                feedid = feed.rowid
            elif feed.rowid != feedid:
                raise FeedException("feed.rowid = %s / feedid = %s" % (feed.rowid, feedid))
        data["feedid"] = feedid
        result = super(FeedEntry, cls).__new__(cls, transaction, rowid, **data)
        result.__feed = feed
        return result

    def __getattr__(self, name):
        if name == "feed":
            return self.__feed
        return super(FeedEntry, self).__getattr__(name)

    def __setattr__(self, name, value):
        if name == "feed":
            self.__feed = value
            seld.feedid = value.rowid
        else:
            super(FeedEntry, self).__setattr__(name, value)
