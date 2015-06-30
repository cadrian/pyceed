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
			yield from cls.__select_or_insert(transaction, rowid=rowid, insert=insert, **values)
		except:
			logging.exception("new %s", cls.__name__)
			raise

	@classmethod
	def __select_or_insert(cls, transaction, rowid=None, insert=None, **values):
		result = None
		cursor = transaction.cursor

		logging.debug("~~>~~ %s(rowid=%s, insert=%s, %s)", cls.__name__, rowid, insert, values)

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
			logging.debug(">>>> %s", query)
			cursor.execute(query)

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
			logging.debug(">>>> %s\n%s", query, values)
			ex = cursor.execute(query, values)
			if ex:
				found = False
				for row in ex:
					logging.debug("++++ %s", row)
					for res in cls(transaction, rowid=row[0], insert=False, **values):
						yield res._update(**extra)
						found = True
				if found and not insert:
					logging.debug("~~<~~ (no rowid, found rows, insert is not True)")
					return
		else:
			result = instances.get(rowid, None)

		if result is None:
			data = {k: None for k in columns}

			if rowid is None:
				if insert is False:
					logging.debug("~~<~~ (no rowid, found 0 rows, insert is False)")
					return
				data.update(values)
				query = "insert into %s (%s) values (%s)" % (
					cls._tablename(),
					", ".join(cls._columnname(c) for c in columns),
					", ".join(":%s" % (k,) for k in columns),
				)
				logging.debug(">>>> %s\n%s", query, data)
				cursor.execute(query, data)
				new_rowid = cursor.getconnection().last_insert_rowid()
			else:
				new_rowid = rowid
				query = "select %s from %s where rowid = ?" % (
					", ".join(cls._columnname(c) for c in columns),
					cls._tablename(),
				)
				logging.debug(">>>> %s\n%s", query, rowid)
				rows = cursor.execute(query, (rowid,))
				for row in rows:
					logging.debug("++++ %s", row)
					for i, col in enumerate(columns):
						data[col] = row[i]
					break
				else:
					# Don't insert a new row if the rowid is provided; in that case,
					# if the row does not exist None must be returned
					logging.debug("~~<~~ (rowid=%s, found 0 rows)", new_rowid)
					return
				list(rows)

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

		logging.debug("~~<~~ (otherwise)")
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
			logging.debug(">>>> %s\n%s", query, data)
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
