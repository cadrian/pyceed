import unittest
from mockito import mock, when, verify, verifyNoMoreInteractions, inorder
from pyceed.db import Filter, Feed

import datetime


class TestFilter(unittest.TestCase):
	"""
	Test Filter
	"""

	def setUp(self):
		self.transaction = mock()
		self.transaction._map = {}
		self.cursor = mock()
		self.connection = mock()
		self.transaction.cursor = self.cursor
		when(self.cursor).getconnection().thenReturn(self.connection)

	def _new_entry(self, published_day):
		result = mock()
		result.rowid = published_day
		result.published = datetime.date(2015, 6, published_day)
		return result

	def test_entries(self):
		definition = "Sort(Union(Truncate(Feed('foo/bar1'), 5), Truncate(Feed('foo/bar2'), 7)), 'published', reverse=True)"

		bar1entry1 = self._new_entry(11)
		bar1entry2 = self._new_entry(22)
		bar1entry3 = self._new_entry(13)
		bar1entry4 = self._new_entry(24)
		bar1entry5 = self._new_entry(15)
		bar1entry6 = self._new_entry(26)
		bar1entry7 = self._new_entry(17)
		bar1entry8 = self._new_entry(28)
		bar1entry9 = self._new_entry(19)

		bar2entry1 = self._new_entry(21)
		bar2entry2 = self._new_entry(12)
		bar2entry3 = self._new_entry(23)
		bar2entry4 = self._new_entry(14)
		bar2entry5 = self._new_entry(25)
		bar2entry6 = self._new_entry(16)
		bar2entry7 = self._new_entry(27)
		bar2entry8 = self._new_entry(18)
		bar2entry9 = self._new_entry(29)

		def iter1entries():
			yield bar1entry1
			yield bar1entry2
			yield bar1entry3
			yield bar1entry4
			yield bar1entry5
			yield bar1entry6
			yield bar1entry7
			yield bar1entry8
			yield bar1entry9
		feed1 = mock()
		feed1.rowid = 1
		when(feed1).entries().thenReturn(iter1entries())
		def iter1():
			yield feed1
		when(self.transaction).select_all(Feed, url='foo/bar1').thenReturn(iter1())

		def iter2entries():
			yield bar2entry1
			yield bar2entry2
			yield bar2entry3
			yield bar2entry4
			yield bar2entry5
			yield bar2entry6
			yield bar2entry7
			yield bar2entry8
			yield bar2entry9
		feed2 = mock()
		feed2.rowid = 2
		when(feed2).entries().thenReturn(iter2entries())
		def iter2():
			yield feed2
		when(self.transaction).select_all(Feed, url='foo/bar2').thenReturn(iter2())

		self.transaction._map[Feed] = {
			1: feed1,
			2: feed2,
		}

		when(self.cursor).execute("select rowid from Filter where definition = :definition", {"definition": definition}).thenReturn([])
		when(self.connection).last_insert_rowid().thenReturn(1)
		when(self.cursor).execute("select rowid from Feed where url = :url", {"url": "foo/bar1"}).thenReturn([(1,)])
		when(self.cursor).execute("select rowid from Feed where url = :url", {"url": "foo/bar2"}).thenReturn([(2,)])

		f = next(Filter(self.transaction, definition=definition))

		entries = [e for e in f.entries()]
		self.assertEqual([
			bar2entry7, # = self._new_entry(27)
			bar2entry5, # = self._new_entry(25)
			bar1entry4, # = self._new_entry(24)
			bar2entry3, # = self._new_entry(23)
			bar1entry2, # = self._new_entry(22)
			bar2entry1, # = self._new_entry(21)
			bar2entry6, # = self._new_entry(16)
			bar1entry5, # = self._new_entry(15)
			bar2entry4, # = self._new_entry(14)
			bar1entry3, # = self._new_entry(13)
			bar2entry2, # = self._new_entry(12)
			bar1entry1, # = self._new_entry(11)
		], entries)

if __name__ == '__main__':
	unittest.main()
