import unittest
from mockito import mock, when, verify, verifyNoMoreInteractions, inorder, any
from pyceed.db.transaction import Transaction


def callable_mock(m=None):
	if m is None:
		m = mock()

	class Mock(object):
		mock = m

		def __new__(self, *a, **kw):
			return m.new(*a, **kw)

		def __getattr__(self, method_name):
			return m.__getattr__(method_name)

	return Mock


def managed_mock(m=None):
	if m is None:
		m = mock()

	class Mock(object):
		mock = m

		def __enter__(self):
			return m.__enter__()

		def __exit__(self, *a, **kw):
			return m.__exit__(*a, **kw)

		def __getattr__(self, method_name):
			return m.__getattr__(method_name)

	return Mock()


class TestTransaction(unittest.TestCase):
	"""
	Test transactional stuff
	"""

	def setUp(self):
		self.factory = callable_mock()
		self.connection = managed_mock()
		self.cursor = mock()
		when(self.connection.mock).cursor().thenReturn(self.cursor)

	@unittest.skip("blinking")
	def test_select(self):
		x = object()
		def iterx():
			yield x
		transaction = Transaction(self.connection)
		inorder.verify(self.connection.mock).cursor()

		when(self.factory.mock).new(transaction=transaction, rowid=42, insert=None, x="foo").thenReturn(iterx())

		fdo = transaction.select(self.factory, rowid=42, x="foo")

		self.assertTrue(fdo is x)

		inorder.verify(self.connection.mock).__enter__()
		inorder.verify(self.connection.mock).__exit__(any(), any(), any())
		verifyNoMoreInteractions(self.connection.mock)

	@unittest.skip("blinking")
	def test_select_all(self):
		x = object()
		def iterx():
			yield x
		transaction = Transaction(self.connection)
		inorder.verify(self.connection.mock).cursor()

		when(self.factory.mock).new(transaction=transaction, insert=None, x="foo").thenReturn(iterx())

		fdo = next(transaction.select_all(self.factory, x="foo"))

		self.assertTrue(fdo is x)

		inorder.verify(self.connection.mock).__enter__()
		inorder.verify(self.connection.mock).__exit__(any(), any(), any())
		verifyNoMoreInteractions(self.connection.mock)

	def test_commit(self):
		fdo = mock()
		fdo.rowid = 42
		fdo.x = "foo"

		transaction = Transaction(self.connection)
		instances = {42: fdo}
		transaction._map[object] = instances
		when(self.factory.mock).new(transaction=transaction, x="foo").thenReturn(fdo)

		transaction.commit()

		inorder.verify(self.connection.mock).cursor()
		inorder.verify(self.connection.mock).__enter__()
		inorder.verify(fdo).commit()
		inorder.verify(self.connection.mock).__exit__(None, None, None)
		verifyNoMoreInteractions(fdo, self.factory.mock, self.connection.mock)

	def test_rollback(self):
		fdo = mock()
		fdo.rowid = 42
		fdo.x = "foo"

		transaction = Transaction(self.connection)
		instances = {42: fdo}
		transaction._map[object] = instances
		when(self.factory.mock).new(transaction=transaction, x="foo").thenReturn(fdo)

		transaction.rollback()

		inorder.verify(self.connection.mock).cursor()
		inorder.verify(fdo).rollback()
		verifyNoMoreInteractions(fdo, self.factory.mock, self.connection.mock)


if __name__ == '__main__':
	unittest.main()
