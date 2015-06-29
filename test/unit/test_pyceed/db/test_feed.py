import logging
import unittest
from mockito import mock, when, verify, verifyNoMoreInteractions, inorder
from pyceed.db import Feed, FeedEntry, FeedException


class TestFeed(unittest.TestCase):
	"""
	Test Feed and FeedEntry
	"""

	def setUp(self):
		logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] <%(threadName)s> %(message)s')
		self.transaction = mock()
		self.transaction._map = {}
		self.cursor = mock()
		self.connection = mock()
		self.transaction.cursor = self.cursor
		when(self.cursor).getconnection().thenReturn(self.connection)

	def test_create_feed_no_url(self):
		with self.assertRaises(FeedException):
			Feed(self.transaction, insert=True)

	def test_create_feed(self):
		def iter(*a):
			for o in a:
				yield (o,)

		when(self.connection).last_insert_rowid().thenReturn(42).thenReturn(1).thenReturn(13).thenReturn(None)
		when(self.cursor).execute('select rowid from main."PyCeedFeed" where "Feed_url" = :url', {
			"url": "foo://bar"
		}).thenReturn([])
		when(self.cursor).execute('select rowid from main."PyCeedFeedEntry" where "FeedEntry_feedid" = :feedid', {
			"feedid": 42
		}).thenReturn(iter()).thenReturn(iter()).thenReturn(iter(1)).thenReturn(iter(1,13))

		f = Feed(self.transaction, url="foo://bar")
		feed = next(f)
		self.assertEqual([], list(f))
		self.assertEqual([], [o for o in FeedEntry(self.transaction, feed=feed, insert=False)])
		f = FeedEntry(self.transaction, feed=feed)
		feed_entry_1 = next(f)
		self.assertEqual([], list(f))

		f = FeedEntry(self.transaction, feed=feed, insert=True)
		f1 = next(f)
		self.assertTrue(f1 is feed_entry_1)
		feed_entry_2 = next(f)
		self.assertEqual([], list(f))

		self.assertFalse(feed_entry_2 is feed_entry_1)

		def iter():
			yield feed_entry_1
			yield feed_entry_2
		when(self.transaction).select_all(FeedEntry, feedid=42).thenReturn(iter())

		entries_gen = feed.entries()
		entries = [e for e in entries_gen]
		self.assertEqual(2, len(entries))
		self.assertTrue(feed_entry_1 in entries)
		self.assertTrue(feed_entry_2 in entries)


if __name__ == '__main__':
	unittest.main()
