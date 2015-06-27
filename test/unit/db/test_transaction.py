import unittest
from mockito import mock, when, verify, verifyNoMoreInteractions, inorder, any
from pyceed.db.transaction import Transaction

class CallableMock(object):
	def __init__(self, m=None):
		self.mock = m or mock()

	def __call__(self, *a, **kw):
		return self.mock.__call__(*a, **kw)

	def __enter__(self):
		return self.mock.__enter__()

	def __exit__(self, *a, **kw):
		return self.mock.__exit__(*a, **kw)

	def __getattr__(self, method_name):
		return self.mock.__getattr__(method_name)

class TestTransaction(unittest.TestCase):
	"""
	Test transactional stuff
	"""

	def setUp(self):
		self.factory = CallableMock()
		self.connection = CallableMock()
		self.cursor = mock()
		when(self.connection.mock).cursor().thenReturn(self.cursor)

	def test_select(self):
		x = object()
		def iterx():
			yield x
		transaction = Transaction(self.connection)
		when(self.factory.mock).__call__(transaction=transaction, insert=None, x="foo").thenReturn([x])

		fdo = next(transaction.select_all(self.factory, x="foo"))

		self.assertTrue(fdo is x)

		inorder.verify(self.connection.mock).cursor()
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
		when(self.factory.mock).__call__(transaction=transaction, x="foo").thenReturn(fdo)

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
		when(self.factory.mock).__call__(transaction=transaction, x="foo").thenReturn(fdo)

		transaction.rollback()

		inorder.verify(self.connection.mock).cursor()
		inorder.verify(fdo).rollback()
		verifyNoMoreInteractions(fdo, self.factory.mock, self.connection.mock)
