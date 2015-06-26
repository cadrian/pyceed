class DbException(Exception):
    pass

class _DbObject(object):
    """
    Parent of all database objects.
    """

    def __new__(cls, transaction, rowid=None, **values):
        """
        Make sure that an instance with a given rowid is always the same instance
        """
        result = None

        columns = cls._columns
        extra = dict()
        for k,v in values.items():
            if not k in columns:
                extra[k] = v
        for k in extra.keys():
            del values[k]

        instances = transaction._map.get(cls, None)
        if instances is None:
            instances = transaction._map[cls] = dict()
            transaction.cursor.execute("create table if not exists %s (%s)" % (cls.__name__, ", ".join(columns)))

        if rowid is not None:
            result = instances.get(rowid, None)
        elif values:
            for row in transaction.cursor.execute("select rowid from %s where %s" % (
                cls.__name__,
                " and ".join("%s = :%s" % (k,k) for k in values.keys()),
            ), values):
                if rowid is not None:
                    raise DbException("More than one row for %s" % (
                        ", ".join("%s = %s" % (k,v) for (k,v) in values.items()),
                    ))
                rowid = row[0]
                result = instances.get(rowid, None)

        if result:
            result.update(**values)
        else:
            data = {k: None for k in columns}

            if rowid is None:
                data.update(values)
                transaction.cursor.execute("insert into %s (%s) values (%s)" % (
                    cls.__name__,
                    ", ".join(columns),
                    ", ".join(":%s" % (k,) for k in columns),
                ), data)
                rowid = transaction.cursor.getconnection().last_insert_rowid()
            else:
                for row in transaction.cursor.execute("select %s from %s where rowid = ?" % (
                        ", ".join(columns),
                        cls.__name__,
                    ), (
                        rowid,
                    )):
                    for i, col in enumerate(columns):
                        data[col] = row[i]

            result = super(_DbObject, cls).__new__(cls)
            result.__rowid = rowid
            result.__data = data
            result.__olddata = dict(data)
            result.__transaction = transaction

            instances[rowid] = result

        result.update(**extra)
        return result

    def __eq__(self, other):
        return other is self

    def update(self, **values):
        for k,v in values.items():
            setattr(self, k, v)

    def commit(self):
        if self.__olddata != self.__data:
            data = {k:v for k,v in self.__data.items() if v != self.__olddata[k]}
            data["rowid"] = self.__rowid
            self.__transaction.cursor.execute("update %s set %s where rowid = :rowid" % (
                type(self).__name__,
                ", ".join("%s = :%s" % (k,k) for k in self._columns if k in data),
            ), data)
            self.__olddata.update(self.__data)

    def rollback(self):
        self.__data.update(self.__olddata)

    def __getattr__(self, name):
        if name == "rowid":
            return self.__rowid
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
