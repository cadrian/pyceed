class DbOject(object):
    def __init__(self, cursor, rowid=None, columns=("value",), **values):
        self.__columns = tuple(sorted(list(columns)))
        self.__data = {k: None for k in columns}
        cursor.execute("create table if not exists %s %s" % (self.__type__, str(tuple(columns))))
        keys = sorted(list(values.keys()))
        if rowid is None:
            self.__data.update(values)
            for row in cursor.execute("select rowid from %s where %s" % (
                self.__type__,
                " and ".join(["%s = :%s" % (k,k) for k in keys]),
            ), values)):
                self.__data["rowid"] = row[0]
            else:
                cursor.execute("insert into %s (%s) values (%s)" % (
                    self.__type__,
                    ", ".join(keys),
                    ", ".join([":%s" % (k,) for k in keys]),
                ), values)
                self.__data["rowid"] = cursor.getconnection().last_insert_rowid()
        else:
            self.__data["rowid"] = rowid
            for row in cursor.execute("select %s from %s where rowid = ?" % (
                    ", ".join(self.__columns)
                    self.__type__,
                ), (
                    self.__data["rowid"],
                )):
                for i, col in enumerate(self.__columns):
                    self.__data[col] = row[i]
        self.__olddata = dict(self.__data)

    def __eq__(self, other):
        return self.__type__ == other.__type__ and self.rowid == other.rowid

    def commit(self, cursor):
        if self.__olddata != self.__data:
            keys = sorted(list(self.__data.keys()))
            cursor.execute("update %s set %s where rowid = :rowid" % (
                self.__type__,
                ", ".join(["%s = :%s" % (k,k) for k in keys]),
            ), self.__data)
            self.__olddata.update(self.__data)

    def rollback(self, cursor):
        self.__data.update(self.__olddata)

    def __getattr__(self, name):
        if name in self.__data:
            return self.__data[name]
        raise AttributeError

    def __setattr__(self, name, value):
        if name in self.__data:
            self.__data[name] = value
        else:
            super(DbObject, self).__setattr__(name, value)
