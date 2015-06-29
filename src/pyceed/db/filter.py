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
from pyceed.db.feed import Feed
from pyceed.oper import MultiFeed, FeedSort, FeedTruncate, FeedRegex


class FilterException(DbException):
	pass


class Filter(_DbObject):
	_columns = ("name", "definition", "title", "subtitle")

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
