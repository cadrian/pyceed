# Filter: the filtered entries

from pyceed.db.internals import DbException, _DbObject
from pyceed.db.feed import Feed
from pyceed.operator import *


class FilterException(DbException):
	pass


class Filter(_DbObject):
	_columns = ("name", "definition")

	def __new__(cls, transaction, rowid=None, definition=None, **data):
		if rowid is None:
			if definition is None:
				raise FilterException("url is needed")
		data["definition"] = definition
		return super(Filter, cls).__new__(cls, transaction, rowid, **data)

	def entries(self):
		def get_feed(url):
			result = next(self.transaction.select_all(Feed, url=url))
			return result
		fil = eval(self.definition, {
			"Feed": get_feed,
			"Union": MultiFeed,
			"Sort": FeedSort,
			"Truncate": FeedTruncate,
			"Regex": FeedRegex,
		})
		return fil.entries()
