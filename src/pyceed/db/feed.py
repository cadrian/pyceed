#  This file is part of PyCeed.
#
#  PyCeed is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3 of the License.
#
#  PyCeed is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PyCeed.  If not, see <http://www.gnu.org/licenses/>.

from pyceed.db.internals import DbException, _DbObject
import pickle
import feedparser


class FeedException(DbException):
	pass


class Feed(_DbObject):
	_columns = ("url", "etag", "modified")

	def __new__(cls, transaction, rowid=None, url=None, insert=None, **data):
		if rowid is None and insert is True:
			if url is None:
				raise FeedException("url is needed")
		if url is not None:
			data["url"] = url
		data["insert"] = insert
		return super(Feed, cls).__new__(cls, transaction, rowid, **data)

	def entries(self):
		yield from self.transaction.select_all(FeedEntry, feedid=self.rowid, insert=False)

	def _feed(self):
		feed = feedparser.parse(self.url, etag=self.etag, modified=self.modified)
		self.etag = getattr(feed, 'etag', None)
		self.modified = getattr(feed, 'modified', None)
		return feed

	def update(self):
		feed = self._feed()
		for entry in feed.entries:
			e = self.transaction.select_unique(FeedEntry, id=entry.id, feed=self)
			e._update(definition=entry)


class FeedEntry(_DbObject):
	_columns = ("definition", "id", "feedid")

	def __new__(cls, transaction, rowid=None, definition=None, feed=None, feedid=None, insert=None, **data):
		if feed is None:
			if feedid is not None:
				feed = transaction.select(Feed, feedid)
		elif feedid is None:
			feedid = feed.rowid

		if rowid is None and insert is True:
			if feed is None:
				raise FeedException("feed or feedid is needed")
			elif feed.rowid != feedid:
				raise FeedException("feed.rowid = %s / feedid = %s" % (feed.rowid, feedid))

		if definition is not None:
			data["definition"] = pickle.dumps(definition)
		if feed is not None:
			data["feed"] = feed
			data["feedid"] = feedid
		if insert is not None:
			data["insert"] = insert
		return super(FeedEntry, cls).__new__(cls, transaction, rowid, **data)

	def __getattr__(self, name):
		if name == "feed":
			return self.__feed
		elif name == "definition":
			definition = super(FeedEntry, self).__getattr__(name)
			if definition is not None:
				return pickle.loads(definition)
		else:
			return super(FeedEntry, self).__getattr__(name)

	def __setattr__(self, name, value):
		if name == "feed":
			self.__feed = value
			super(FeedEntry, self).__setattr__(name, value.rowid)
		elif name == "definition":
			super(FeedEntry, self).__setattr__(name, pickle.dumps(value))
		else:
			super(FeedEntry, self).__setattr__(name, value)
