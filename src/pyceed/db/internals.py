class DbException(Exception):
	pass


class _DbObject(object):
	"""
	Parent of all database objects.
	"""

	def __new__(cls, transaction, rowid=None, insert=None, **values):
		"""
		Make sure that an instance with a given rowid is always the same instance.

		If rowid is None, will return a list of all the objects that match the values
		Otherwise, will return either the object if it exists in the database, or None
		"""
		result = None

		columns = cls._columns
		extra = { k:v for k,v in values.items() if not k in columns }
		for k in extra.keys():
			del values[k]

		instances = transaction._map.get(cls, None)
		if instances is None:
			instances = transaction._map[cls] = dict()
			query = "create table if not exists %s (%s)" % (
				cls.__name__,
				 ", ".join(columns),
			)
			transaction.cursor.execute(query)

		if rowid is None:
			if values and not insert:
				query = "select rowid from %s where %s" % (
					cls.__name__,
					" and ".join("%s = :%s" % (k,k) for k in values.keys()),
				)
				ex = transaction.cursor.execute(query, values)
				results = [ cls(transaction, rowid=row[0], **values).update(**extra) for row in ex ]
				if results:
					return results
		else:
			result = instances.get(rowid, None)

		if result is None:
			data = {k: None for k in columns}

			if rowid is None:
				if insert is False:
					return []
				data.update(values)
				query = "insert into %s (%s) values (%s)" % (
					cls.__name__,
					", ".join(columns),
					", ".join(":%s" % (k,) for k in columns),
				)
				transaction.cursor.execute(query, data)
				new_rowid = transaction.cursor.getconnection().last_insert_rowid()
			else:
				new_rowid = rowid
				query = "select %s from %s where rowid = ?" % (
					", ".join(columns),
					cls.__name__,
				)
				for row in transaction.cursor.execute(query, (
						rowid,
					)):
					for i, col in enumerate(columns):
						data[col] = row[i]
					break
				else:
					# Don't insert a new row if the rowid is provided; in that case,
					# if the row does not exist None must be returned
					return None

			result = super(_DbObject, cls).__new__(cls)
			result.__rowid = new_rowid
			result.__data = data
			result.__olddata = dict(data)
			result.__transaction = transaction

			instances[new_rowid] = result
		else:
			result.update(**values)

		result.update(**extra)
		if rowid is None:
			return [result]
		else:
			return result

	def __eq__(self, other):
		return other is self

	def update(self, **values):
		for k,v in values.items():
			setattr(self, k, v)
		return self

	def commit(self):
		if self.__olddata != self.__data:
			data = {k:v for k,v in self.__data.items() if v != self.__olddata[k]}
			data["rowid"] = self.__rowid
			query = "update %s set %s where rowid = :rowid" % (
				type(self).__name__,
				", ".join("%s = :%s" % (k,k) for k in self._columns if k in data),
			)
			self.transaction.cursor.execute(query, data)
			self.__olddata.update(self.__data)

	def rollback(self):
		self.__data.update(self.__olddata)

	def __getattr__(self, name):
		if name == "rowid":
			return self.__rowid
		elif name == "transaction":
			return self.__transaction
		elif name in self.__data:
			return self.__data[name]
		else:
			raise AttributeError

	def __setattr__(self, name, value):
		if name.startswith('_'):
			super(_DbObject, self).__setattr__(name, value)
		elif name == "rowid":
			raise AttributeError("rowid cannot be changed")
		elif name in self.__data:
			self.__data[name] = value
		else:
			super(_DbObject, self).__setattr__(name, value)
