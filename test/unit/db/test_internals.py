import unittest
from mockito import mock, when, verify, verifyNoMoreInteractions, inorder
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

		fdo = next(FakeDbObject(self.transaction))

		inorder.verify(self.cursor, times=1).execute("create table if not exists FakeDbObject (timestamp, value)")
		inorder.verify(self.cursor, times=1).execute("insert into FakeDbObject (timestamp, value) values (:timestamp, :value)", {
			"timestamp": None,
			"value": None,
		})
		inorder.verify(self.cursor, times=1).getconnection()
		inorder.verify(self.connection, times=1).last_insert_rowid()
		verifyNoMoreInteractions(self.cursor, self.connection)
		self.assertIsNone(fdo.value)
		self.assertIsNone(fdo.timestamp)
		self.assertTrue(fdo.rowid == 42)
		self.assertEqual({FakeDbObject: {42: fdo}}, self.transaction._map)

	def test_create_same(self):
		when(self.connection).last_insert_rowid().thenReturn(42)

		fdo = next(FakeDbObject(self.transaction))

		inorder.verify(self.cursor, times=1).execute("create table if not exists FakeDbObject (timestamp, value)")
		inorder.verify(self.cursor, times=1).execute("insert into FakeDbObject (timestamp, value) values (:timestamp, :value)", {
			"timestamp": None,
			"value": None,
		})
		inorder.verify(self.cursor, times=1).getconnection()
		inorder.verify(self.connection, times=1).last_insert_rowid()

		fdo2 = next(FakeDbObject(self.transaction, rowid=42))
		verifyNoMoreInteractions(self.cursor, self.connection)

		self.assertTrue(fdo is fdo2)

	def test_create_commit(self):
		when(self.connection).last_insert_rowid().thenReturn(42)

		fdo = next(FakeDbObject(self.transaction))

		inorder.verify(self.cursor, times=1).execute("create table if not exists FakeDbObject (timestamp, value)")
		inorder.verify(self.cursor, times=1).execute("insert into FakeDbObject (timestamp, value) values (:timestamp, :value)", {
			"timestamp": None,
			"value": None,
		})
		inorder.verify(self.cursor, times=1).getconnection()
		inorder.verify(self.connection, times=1).last_insert_rowid()

		fdo2 = next(FakeDbObject(self.transaction, rowid=42, value="foobar"))
		verifyNoMoreInteractions(self.cursor, self.connection)

		self.assertEqual("foobar", fdo.value)
		self.assertTrue(fdo is fdo2)

		fdo.commit()
		inorder.verify(self.cursor, times=1).execute("update FakeDbObject set value = :value where rowid = :rowid", {
			"value": "foobar",
			"rowid": 42,
		})
		verifyNoMoreInteractions(self.cursor, self.connection)

	def test_create_rollback(self):
		when(self.connection).last_insert_rowid().thenReturn(42)

		fdo = next(FakeDbObject(self.transaction))

		inorder.verify(self.cursor, times=1).execute("create table if not exists FakeDbObject (timestamp, value)")
		inorder.verify(self.cursor, times=1).execute("insert into FakeDbObject (timestamp, value) values (:timestamp, :value)", {
			"timestamp": None,
			"value": None,
		})
		inorder.verify(self.cursor, times=1).getconnection()
		inorder.verify(self.connection, times=1).last_insert_rowid()

		fdo2 = next(FakeDbObject(self.transaction, rowid=42, value="foobar"))
		verifyNoMoreInteractions(self.cursor, self.connection)

		self.assertEqual("foobar", fdo.value)
		self.assertTrue(fdo is fdo2)

		fdo.rollback()
		verifyNoMoreInteractions(self.cursor, self.connection)

		self.assertIsNone(fdo.value)

	def test_select_one(self):
		when(self.cursor).execute("select timestamp, value from FakeDbObject where rowid = ?", (42,)).thenReturn([(None,"foobar")]).thenReturn(None)

		fdo = next(FakeDbObject(self.transaction, rowid=42))
		self.assertTrue(type(fdo) is FakeDbObject)

		self.assertEqual("foobar", fdo.value)
		self.assertIsNone(fdo.timestamp)
		self.assertTrue(fdo.rowid == 42)
		self.assertEqual({FakeDbObject: {42: fdo}}, self.transaction._map)

		fdo2 = next(FakeDbObject(self.transaction, rowid=42))
		self.assertTrue(fdo is fdo2)

	def test_select_many(self):
		when(self.cursor).execute("select rowid from FakeDbObject where value = :value", {
			"value": "foobar",
		}).thenReturn([(1,),(13,)]).thenReturn(None)
		when(self.cursor).execute("select timestamp, value from FakeDbObject where rowid = ?", (1,)).thenReturn([("ts1", "foobar")]).thenReturn(None)
		when(self.cursor).execute("select timestamp, value from FakeDbObject where rowid = ?", (13,)).thenReturn([("ts13", "foobar")]).thenReturn(None)

		fdos = FakeDbObject(self.transaction, value="foobar")

		fdo0 = next(fdos)
		self.assertEqual(1, fdo0.rowid)
		self.assertEqual("ts1", fdo0.timestamp)
		self.assertEqual("foobar", fdo0.value)

		fdo1 = next(fdos)
		self.assertEqual(13, fdo1.rowid)
		self.assertEqual("ts13", fdo1.timestamp)
		self.assertEqual("foobar", fdo1.value)

		self.assertRaises(StopIteration, next, fdos)


if __name__ == '__main__':
	unittest.main()
