# Transaction: a central point of control for database objects with commit / rollback management

from pyceed.db.internals import DbException, _DbObject


class Transaction(object):
	def __init__(self, connection):
		"""
		Create a new transaction bound to the given connection which must be compatible with apsw's
		"""
		self.__connection = connection
		self.__cursor = connection.cursor()
		self._map = {}

	def select(self, factory, rowid, **kw):
		"""
		Select an object of the given factory, create it if not found.
		Register and return that object.
		"""
		with self.__connection:
			return factory(transaction=self, rowid=rowid, insert=None, **kw)

	def select_all(self, factory, rowid=None, insert=None, **kw):
		"""
		Select a list of objects of the given factory, create them if not found.
		Register and return those objects.

		Variants:
		* If rowid is specified, will return at most one object
		* If insert=True, will always create a new object
		* If insert=False, will never create a new object
		"""
		result = None
		with self.__connection:
			result = factory(transaction=self, rowid=rowid, insert=insert, **kw)
		if rowid is not None:
			if result:
				result = [result]
			else:
				result = []
		return result

	def commit(self):
		"""
		Commit all registered objects
		"""
		with self.__connection:
			for obj in self.items():
				obj.commit()

	def rollback(self):
		"""
		Rollback all the registered objects
		"""
		for obj in self.items():
			obj.rollback()

	def items(self):
		"""
		Iterate over all the registered objects
		"""
		for instances in self._map.values():
			for instance in instances.values():
				yield instance

	def __getattr__(self, name):
		if name == "cursor":
			return self.__cursor
		else:
			return super(Transaction, self).__getattr__(name)
