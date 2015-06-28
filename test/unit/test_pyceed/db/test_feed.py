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
		with self.assertRaises(FeedException):
			Feed(self.transaction)

	def test_create_feed(self):
		when(self.connection).last_insert_rowid().thenReturn(42).thenReturn(1).thenReturn(13).thenReturn(None)
		when(self.cursor).execute("select rowid from Feed where url = :url", {
			"url": "foo://bar"
		}).thenReturn([])
		when(self.cursor).execute("select rowid from FeedEntry where feedid = :feedid", {
			"feedid": 42
		}).thenReturn([]).thenReturn([]).thenReturn([(1,)]).thenReturn([(1,),(13,)])

		feed = next(Feed(self.transaction, url="foo://bar"))
		self.assertEqual([], [o for o in FeedEntry(self.transaction, feed=feed, insert=False)])
		feed_entry_1 = next(FeedEntry(self.transaction, feed=feed))

		entries = FeedEntry(self.transaction, feed=feed, insert=True)
		self.assertTrue(next(entries) is feed_entry_1)
		feed_entry_2 = next(entries)

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
