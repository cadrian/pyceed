import unittest
from mockito import mock, when, verify, verifyNoMoreInteractions, inorder
from pyceed.operator import MultiFeed


class TestMultiFeed(unittest.TestCase):
	"""
	Test MultiFeed
	"""

	def test_entries(self):
		def iterx():
			yield 'foo'
			yield 'bar'
		x = mock()
		x.entries = iterx
		x.rowid = 1

		def itery():
			yield 1
			yield 2
		y = mock()
		y.entries = itery
		y.rowid = 2

		multi = MultiFeed()
		multi.add_feed(x)
		multi.add_feed(y)

		entries = [entry for entry in multi.entries()]
		self.assertEqual(["foo", "bar", 1, 2], entries)


if __name__ == '__main__':
	unittest.main()
