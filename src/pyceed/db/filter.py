# Filter: the filtered entries

from pyceed.db.internals import DbException, _DbObject
from pyceed.db.feed import Feed
from pyceed.oper import MultiFeed, FeedSort, FeedTruncate, FeedRegex


class FilterException(DbException):
	pass


class Filter(_DbObject):
	_columns = ("name", "definition")

	def __new__(cls, transaction, rowid=None, definition=None, name=None, insert=None, **data):
		if rowid is None and insert is True:
			if definition is None:
				raise FilterException("definition is needed")
			if name is None:
				raise FilterException("name is needed")
		if name is not None:
			data["name"] = name
		if definition is not None:
			data["definition"] = definition
		data["insert"] = insert
		return super(Filter, cls).__new__(cls, transaction, rowid, **data)

	def _filter(self):
		def get_feed(url):
			return self.transaction.select_unique(Feed, url=url)
		return eval(self.definition, {
			"Feed": get_feed,
			"Union": MultiFeed,
			"Sort": FeedSort,
			"Truncate": FeedTruncate,
			"Regex": FeedRegex,
		})

	def entries(self):
		yield from self._filter().entries()

	def update(self):
		self._filter().update()
