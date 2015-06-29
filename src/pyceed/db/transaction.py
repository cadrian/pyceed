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

import logging


class TransactionException(Exception):
	pass


class Transaction(object):
	def __init__(self, connection):
		"""
		Create a new transaction bound to the given connection which must be compatible with apsw's
		"""
		self.__connection = connection
		self._map = {}
		with self:
			self.cursor.execute("pragma foreign_keys = 1; pragma integrity_check")

	def select(self, factory, rowid, **kw):
		"""
		Select an object of the given factory, create it if not found.
		Register and return that object.
		"""
		with self:
			f = factory(transaction=self, rowid=rowid, insert=None, **kw)
			result = next(f)
			list(f)
			return result

	def select_unique(self, factory, rowid=None, insert=None, **kw):
		"""
		Return a unique row, or None
		"""
		result = None
		f = self.select_all(factory, rowid=rowid, insert=insert, **kw)
		try:
			for r in f:
				if result is None:
					result = r
				else:
					kw["rowid"] = rowid
					kw["insert"] = insert
					raise TransactionException("not unique: %s%s" % (factory.__name__, kw))
		finally:
			list(f)
		return result

	def select_all(self, factory, rowid=None, insert=None, **kw):
		"""
		Iterate over the selected objects of the given factory, create them if not found.
		Register and yield those objects.

		Variants:
		* If rowid is specified, will yield at most one object
		* If insert=True, will always create a new object
		* If insert=False, will never create a new object
		"""
		with self:
			if rowid is None:
				yield from factory(transaction=self, insert=insert, **kw)
			else:
				yield from factory(transaction=self, rowid=rowid, **kw)

	def commit(self):
		"""
		Commit all registered objects
		"""
		with self:
			for obj in self.items():
				obj.commit()
			for obj in self.items():
				obj._finish_commit()
		self.cursor.execute("pragma foreign_key_check")

	def rollback(self):
		"""
		Rollback all the registered objects
		"""
		with self:
			for obj in self.items():
				obj.rollback()

	def items(self):
		"""
		Iterate over all the registered objects
		"""
		for instances in self._map.values():
			for instance in instances.values():
				yield instance

	def _trace(self, cursor, sql, bindings):
		logging.debug(">>>> %s", sql)
		if bindings:
			logging.debug(".... %s", bindings)
		return True

	def __getattr__(self, name):
		if name == "cursor":
			cursor = self.__connection.cursor()
			cursor.setexectrace(self._trace)
			return cursor
		else:
			return super(Transaction, self).__getattr__(name)

	def __enter__(self, *a, **kw):
		self.__connection.__enter__(*a, **kw)

	def __exit__(self, *a, **kw):
		self.__connection.__exit__(*a, **kw)
