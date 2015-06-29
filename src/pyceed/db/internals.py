import sys, traceback

class DbException(Exception):
	pass


class _DbObject(object):
	"""
	Parent of all database objects.
	"""

	@classmethod
	def _tablename(cls):
		return 'main."PyCeed%s"' % (cls.__name__,)

	@classmethod
	def _columnname(cls, col):
		return '"%s_%s"' % (cls.__name__, col,)

	def __new__(cls, transaction, rowid=None, insert=None, **values):
		"""
		Make sure that an instance with a given rowid is always the same instance.

		If rowid is None, will yield all the objects that match the values
		Otherwise, will either yield the object if it exists in the database, or nothing
		"""
		try:
			return cls.__select_or_insert(transaction, rowid=rowid, insert=insert, **values)
		except:
			traceback.print_exc(file=sys.stdout)
			raise

	@classmethod
	def __select_or_insert(cls, transaction, rowid=None, insert=None, **values):
		result = None

		#print("\n~~>~~ %s(rowid=%s, insert=%s, %s)" % (cls.__name__, rowid, insert, values))

		columns = cls._columns
		extra = { k:v for k,v in values.items() if not k in columns }
		for k in extra.keys():
			del values[k]

		instances = transaction._map.get(cls, None)
		if instances is None:
			instances = transaction._map[cls] = dict()
			query = "create table if not exists %s (%s)" % (
				cls._tablename(),
				 ", ".join(cls._columnname(c) for c in columns),
			)
			#print(">>>> " + query)
			transaction.cursor.execute(query)

		if rowid is None:
			if values:
				query = "select rowid from %s where %s" % (
					cls._tablename(),
					" and ".join('%s = :%s' % (cls._columnname(k),k) for k,v in values.items()),
				)
			else:
				query = "select rowid from %s" % (
					cls._tablename(),
				)
			#print(">>>> " + query + "\n" + str(values))
			ex = transaction.cursor.execute(query, values)
			if ex:
				found = False
				for row in ex:
					for res in cls(transaction, rowid=row[0], **values):
						yield res._update(**extra)
						found = True
				if found and not insert:
					#print("~~<~~ (no rowid, found rows, insert is not True)\n")
					return
		else:
			result = instances.get(rowid, None)

		if result is None:
			data = {k: None for k in columns}

			if rowid is None:
				if insert is False:
					#print("~~<~~ (no rowid, found 0 rows, insert is False)\n")
					return
				data.update(values)
				query = "insert into %s (%s) values (%s)" % (
					cls._tablename(),
					", ".join(cls._columnname(c) for c in columns),
					", ".join(":%s" % (k,) for k in columns),
				)
				#print(">>>> " + query + "\n" + str(data))
				cur = transaction.cursor
				cur.execute(query, data)
				new_rowid = cur.getconnection().last_insert_rowid()
			else:
				new_rowid = rowid
				query = "select %s from %s where rowid = ?" % (
					", ".join(cls._columnname(c) for c in columns),
					cls._tablename(),
				)
				#print(">>>> " + query + "\nrowid=" + str(rowid))
				for row in transaction.cursor.execute(query, (rowid,)):
					for i, col in enumerate(columns):
						data[col] = row[i]
					break
				else:
					# Don't insert a new row if the rowid is provided; in that case,
					# if the row does not exist None must be returned
					#print("~~<~~ (rowid=%s, found 0 rows)\n"% (new_rowid,))
					return

			result = super(_DbObject, cls).__new__(cls)
			result.__rowid = new_rowid
			result.__data = data
			result.__olddata = dict(data)
			result.__transaction = transaction

			instances[new_rowid] = result
		else:
			result._update(**values)

		result._update(**extra)
		yield result

		#print("~~<~~ (otherwise)\n")
		return

	def __eq__(self, other):
		return other is self

	def _update(self, **values):
		for k,v in values.items():
			setattr(self, k, v)
		return self

	def commit(self):
		if self.__olddata != self.__data:
			data = {k:v for k,v in self.__data.items() if v != self.__olddata[k]}
			query = "update %s set %s where rowid = :rowid" % (
				self._tablename(),
				", ".join('%s = :%s' % (self._columnname(k),k) for k in self._columns if k in data),
			)
			#print(">>>> " + query + "\n" + str(data))
			data["rowid"] = self.__rowid
			self.transaction.cursor.execute(query, data)

	def _finish_commit(self):
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
