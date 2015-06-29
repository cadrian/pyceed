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

import unittest
from mockito import mock, when, verify, verifyNoMoreInteractions, inorder
from pyceed.oper import FeedSort, FeedTruncate, FeedRegex


class TestFeedSort(unittest.TestCase):
	"""
	Test FeedSort
	"""

	def test_entries(self):
		foo = mock()
		foo.definition = mock()
		foo.definition.data = "foo"
		bar = mock()
		bar.definition = mock()
		bar.definition.data = "bar"

		def iterentries():
			yield foo
			yield bar
		feed = mock()
		feed.entries = iterentries

		sort = FeedSort(feed=feed, field="data")

		entries = [entry for entry in sort.entries()]
		self.assertEqual([bar, foo], entries)


class TestFeedTruncate(unittest.TestCase):
	"""
	Test FeedTruncate
	"""

	def test_entries(self):
		foo = mock()
		foo.definition = mock()
		foo.definition.data = "foo"
		bar = mock()
		bar.definition = mock()
		bar.definition.data = "bar"

		def iterentries():
			yield foo
			yield bar
		feed = mock()
		feed.entries = iterentries

		trunc = FeedTruncate(feed=feed, limit=1)

		entries = [entry for entry in trunc.entries()]
		self.assertEqual([foo], entries)


class TestFeedRegex(unittest.TestCase):
	"""
	Test FeedRegex
	"""

	def test_entries(self):
		foo = mock()
		foo.definition = mock()
		foo.definition.data = "foo"
		bar = mock()
		bar.definition = mock()
		bar.definition.data = "bar"
		baz = mock()
		baz.definition = mock()
		baz.definition.data = "baz"
		ebaz = mock()
		ebaz.definition = mock()
		ebaz.definition.data = "ebaz"

		def iterentries():
			yield baz
			yield foo
			yield bar
			yield ebaz
		feed = mock()
		feed.entries = iterentries

		rex = FeedRegex(feed=feed, field="data", regex="ba.")

		entries = [entry for entry in rex.entries()]
		self.assertEqual([baz, bar], entries)


if __name__ == '__main__':
	unittest.main()
