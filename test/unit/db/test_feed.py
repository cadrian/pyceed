import unittest
from mockito import mock, when, verify, verifyNoMoreInteractions, inorder
from pyceed.db import Feed, FeedEntry, FeedException

class TestFeed(unittest.TestCase):
	"""
	Test Feed and FeedEntry
	"""

	def setUp(self):
		self.transaction = mock()
		self.transaction._map = {}
		self.cursor = mock()
		self.connection = mock()
		self.transaction.cursor = self.cursor
		when(self.cursor).getconnection().thenReturn(self.connection)

	def test_create_feed_no_url(self):
		self.assertRaises(FeedException, Feed, self.transaction)

	def test_create_feed(self):
		when(self.connection).last_insert_rowid().thenReturn(42).thenReturn(1).thenReturn(13).thenReturn(None)
		when(self.cursor).execute("select rowid from Feed where url = :url", {
			"url": "foo://bar"
		}).thenReturn([])
		when(self.cursor).execute("select rowid from FeedEntry where feedid = :feedid", {
			"feedid": 42
		}).thenReturn([]).thenReturn([(1,)]).thenReturn([(1,),(13,)])

		feed = Feed(self.transaction, url="foo://bar")[0]
		feed_entry_1 = FeedEntry(self.transaction, feed=feed)[0]
		feed_entry_2 = FeedEntry(self.transaction, feed=feed, insert=True)[0]

		self.assertFalse(feed_entry_2 is feed_entry_1)

		when(self.transaction).select(FeedEntry, feedid=42).thenReturn([feed_entry_1, feed_entry_2])

		entries = [e for e in feed.entries()]
		self.assertEqual(2, len(entries))
		self.assertTrue(feed_entry_1 in entries)
		self.assertTrue(feed_entry_2 in entries)
