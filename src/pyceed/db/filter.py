# Filter: the filtered entries

from pyceed.db.internals import DbException, _DbObject
from pyceed.db.feed import Feed
from pyceed.oper import MultiFeed, FeedSort, FeedTruncate, FeedRegex


class FilterException(DbException):
	pass


class Filter(_DbObject):
	_columns = ("name", "definition")

	def __new__(cls, transaction, rowid=None, definition=None, name=None, insert=None, **data):
		if rowid is None:
			if definition is None and insert is True:
				raise FilterException("definition is needed")
			if name is None and insert is True:
				raise FilterException("name is needed")
		data["name"] = name
		data["definition"] = definition
		data["insert"] = insert
		return super(Filter, cls).__new__(cls, transaction, rowid, **data)

	def _filter(self):
		def get_feed(url):
			result = next(self.transaction.select_all(Feed, url=url))
			return result
		return eval(self.definition, {
			"Feed": get_feed,
			"Union": MultiFeed,
			"Sort": FeedSort,
			"Truncate": FeedTruncate,
			"Regex": FeedRegex,
		})

	def entries(self):
		return self._filter().entries()

	def update(self):
		self._filter().update()
