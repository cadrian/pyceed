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
from mockito import mock, when, verify, verifyNoMoreInteractions
from pyceed.db.internals import _DbObject


class FakeDbObject(_DbObject):
	_columns = ("timestamp", "value")


class TestDbObject(unittest.TestCase):
	"""
	Test basic DbObject stuff
	"""

	def setUp(self):
		self.transaction = mock()
		self.transaction._map = {}
		self.cursor = mock()
		self.connection = mock()
		self.transaction.cursor = self.cursor
		when(self.cursor).getconnection().thenReturn(self.connection)

	def test_create_empty(self):
		when(self.connection).last_insert_rowid().thenReturn(42)

		f = FakeDbObject(self.transaction)
		fdo = next(f)
		self.assertEqual([], list(f))

		verify(self.cursor, times=1).execute('create table if not exists main."PyCeedFakeDbObject" ("FakeDbObject_timestamp", "FakeDbObject_value")')
		verify(self.cursor, times=1).execute('insert into main."PyCeedFakeDbObject" ("FakeDbObject_timestamp", "FakeDbObject_value") values (:timestamp, :value)', {
			"timestamp": None,
			"value": None,
		})
		verify(self.cursor, times=1).getconnection()
		verify(self.connection, times=1).last_insert_rowid()

		self.assertIsNone(fdo.value)
		self.assertIsNone(fdo.timestamp)
		self.assertTrue(fdo.rowid == 42)
		self.assertEqual({FakeDbObject: {42: fdo}}, self.transaction._map)

	def test_create_same(self):
		when(self.connection).last_insert_rowid().thenReturn(42)

		f = FakeDbObject(self.transaction)
		fdo = next(f)
		self.assertEqual([], list(f))

		verify(self.cursor, times=1).execute('create table if not exists main."PyCeedFakeDbObject" ("FakeDbObject_timestamp", "FakeDbObject_value")')
		verify(self.cursor, times=1).execute('insert into main."PyCeedFakeDbObject" ("FakeDbObject_timestamp", "FakeDbObject_value") values (:timestamp, :value)', {
			"timestamp": None,
			"value": None,
		})
		verify(self.cursor, times=1).getconnection()
		verify(self.connection, times=1).last_insert_rowid()

		f = FakeDbObject(self.transaction, rowid=42)
		fdo2 = next(f)
		self.assertEqual([], list(f))

		self.assertTrue(fdo is fdo2)

	def test_create_commit(self):
		when(self.connection).last_insert_rowid().thenReturn(42)

		f = FakeDbObject(self.transaction)
		fdo = next(f)
		self.assertEqual([], list(f))

		verify(self.cursor, times=1).execute('create table if not exists main."PyCeedFakeDbObject" ("FakeDbObject_timestamp", "FakeDbObject_value")')
		verify(self.cursor, times=1).execute('insert into main."PyCeedFakeDbObject" ("FakeDbObject_timestamp", "FakeDbObject_value") values (:timestamp, :value)', {
			"timestamp": None,
			"value": None,
		})
		verify(self.cursor, times=1).getconnection()
		verify(self.connection, times=1).last_insert_rowid()

		f = FakeDbObject(self.transaction, rowid=42, value="foobar")
		fdo2 = next(f)
		self.assertEqual([], list(f))

		self.assertEqual("foobar", fdo.value)
		self.assertTrue(fdo is fdo2)

		fdo.commit()
		verify(self.cursor, times=1).execute('update main."PyCeedFakeDbObject" set "FakeDbObject_value" = :value where rowid = :rowid', {
			"value": "foobar",
			"rowid": 42,
		})

	def test_create_rollback(self):
		when(self.connection).last_insert_rowid().thenReturn(42)

		f = FakeDbObject(self.transaction)
		fdo = next(f)
		self.assertEqual([], list(f))

		verify(self.cursor, times=1).execute('create table if not exists main."PyCeedFakeDbObject" ("FakeDbObject_timestamp", "FakeDbObject_value")')
		verify(self.cursor, times=1).execute('insert into main."PyCeedFakeDbObject" ("FakeDbObject_timestamp", "FakeDbObject_value") values (:timestamp, :value)', {
			"timestamp": None,
			"value": None,
		})

		self.assertEqual(42, fdo.rowid)

		f = FakeDbObject(self.transaction, rowid=42, value="foobar")
		fdo2 = next(f)
		self.assertEqual([], list(f))

		self.assertEqual("foobar", fdo.value)
		self.assertTrue(fdo is fdo2)

		fdo.rollback()

		self.assertIsNone(fdo.value)

	def test_select_one(self):
		when(self.cursor).execute('select "FakeDbObject_timestamp", "FakeDbObject_value" from main."PyCeedFakeDbObject" where rowid = ?', (42,)).thenReturn([(None,"foobar")]).thenReturn(None)

		f = FakeDbObject(self.transaction, rowid=42)
		fdo = next(f)
		self.assertEqual([], list(f))
		self.assertTrue(type(fdo) is FakeDbObject)

		self.assertEqual("foobar", fdo.value)
		self.assertIsNone(fdo.timestamp)
		self.assertTrue(fdo.rowid == 42)
		self.assertEqual({FakeDbObject: {42: fdo}}, self.transaction._map)

		f = FakeDbObject(self.transaction, rowid=42)
		fdo2 = next(f)
		self.assertEqual([], list(f))
		self.assertTrue(fdo is fdo2)

	def test_select_many(self):
		when(self.cursor).execute('select rowid from main."PyCeedFakeDbObject" where "FakeDbObject_value" = :value', {
			"value": "foobar",
		}).thenReturn([(1,),(13,)]).thenReturn(None)
		when(self.cursor).execute('select "FakeDbObject_timestamp", "FakeDbObject_value" from main."PyCeedFakeDbObject" where rowid = ?', (1,)).thenReturn([("ts1", "foobar")]).thenReturn(None)
		when(self.cursor).execute('select "FakeDbObject_timestamp", "FakeDbObject_value" from main."PyCeedFakeDbObject" where rowid = ?', (13,)).thenReturn([("ts13", "foobar")]).thenReturn(None)

		f = FakeDbObject(self.transaction, value="foobar")

		fdo0 = next(f)
		self.assertEqual(1, fdo0.rowid)
		self.assertEqual("ts1", fdo0.timestamp)
		self.assertEqual("foobar", fdo0.value)

		fdo1 = next(f)
		self.assertEqual(13, fdo1.rowid)
		self.assertEqual("ts13", fdo1.timestamp)
		self.assertEqual("foobar", fdo1.value)

		self.assertEqual([], list(f))


if __name__ == '__main__':
	unittest.main()
