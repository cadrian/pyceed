import unittest
from mockito import mock, when, verify, verifyNoMoreInteractions, inorder
from pyceed.operator import FeedSort, FeedTruncate, FeedRegex


class TestFeedSort(unittest.TestCase):
	"""
	Test FeedSort
	"""

	def test_entries(self):
		foo = mock()
		foo.data = "foo"
		bar = mock()
		bar.data = "bar"

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
		foo.data = "foo"
		bar = mock()
		bar.data = "bar"

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
		foo.data = "foo"
		bar = mock()
		bar.data = "bar"
		baz = mock()
		baz.data = "baz"
		ebaz = mock()
		ebaz.data = "ebaz"

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
