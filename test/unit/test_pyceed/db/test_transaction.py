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
from mockito import mock, when, verify, verifyNoMoreInteractions, any
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

	def test_select(self):
		x = object()
		def iterx():
			yield x
		transaction = Transaction(self.connection)

		when(self.factory.mock).new(transaction=transaction, rowid=42, insert=None, x="foo").thenReturn(iterx())

		fdo = transaction.select(self.factory, rowid=42, x="foo")

		self.assertTrue(fdo is x)

		verify(self.connection.mock, atleast=1).__enter__()
		verify(self.connection.mock, atleast=1).__exit__(any(), any(), any())

	def test_select_all(self):
		x = object()
		def iterx():
			yield x
		transaction = Transaction(self.connection)

		when(self.factory.mock).new(transaction=transaction, insert=None, x="foo").thenReturn(iterx())

		f = transaction.select_all(self.factory, insert=None, x="foo")
		fdo = next(f)
		self.assertEqual([], list(f))

		self.assertTrue(fdo is x)

		verify(self.connection.mock, atleast=1).__enter__()
		verify(self.connection.mock, atleast=1).__exit__(any(), any(), any())

	def test_commit(self):
		fdo = mock()
		fdo.rowid = 42
		fdo.x = "foo"

		transaction = Transaction(self.connection)
		instances = {42: fdo}
		transaction._map[object] = instances
		when(self.factory.mock).new(transaction=transaction, x="foo").thenReturn(fdo)

		transaction.commit()

		verify(self.connection.mock, atleast=1).__enter__()
		verify(fdo).commit()
		verify(self.connection.mock, atleast=1).__exit__(None, None, None)

	def test_rollback(self):
		fdo = mock()
		fdo.rowid = 42
		fdo.x = "foo"

		transaction = Transaction(self.connection)
		instances = {42: fdo}
		transaction._map[object] = instances
		when(self.factory.mock).new(transaction=transaction, x="foo").thenReturn(fdo)

		transaction.rollback()

		verify(fdo).rollback()


if __name__ == '__main__':
	unittest.main()
