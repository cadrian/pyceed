# Transaction: a central point of control for database objects with commit / rollback management


class TransactionException(Exception):
	pass


class Transaction(object):
	def __init__(self, connection):
		"""
		Create a new transaction bound to the given connection which must be compatible with apsw's
		"""
		self.__connection = connection
		self._map = {}

	def select(self, factory, rowid, **kw):
		"""
		Select an object of the given factory, create it if not found.
		Register and return that object.
		"""
		with self.__connection:
			return next(factory(transaction=self, rowid=rowid, insert=None, **kw))

	def select_unique(self, factory, rowid=None, insert=None, **kw):
		"""
		Return a unique row, or None
		"""
		result = None
		for r in self.select_all(factory, rowid=rowid, insert=insert, **kw):
			if result is None:
				result = r
			else:
				kw["rowid"] = rowid
				kw["insert"] = insert
				raise TransactionException("not unique: %s%s" % (factory.__name__, kw))
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
		with self.__connection:
			if rowid is None:
				for obj in factory(transaction=self, insert=insert, **kw):
					yield obj
			else:
				yield factory(transaction=self, rowid=rowid, **kw)

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
		with self.__connection:
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
		print(">>>> " + sql)
		if bindings:
			print(".... " + str(bindings))
		return True

	def __getattr__(self, name):
		if name == "cursor":
			cursor = self.__connection.cursor()
			cursor.setexectrace(self._trace)
			return cursor
		else:
			return super(Transaction, self).__getattr__(name)
