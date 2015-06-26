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

    def select(self, factory, **kw):
        """
        Select an object of the given factory, create it if not found.
        Register and return that object.
        """
        with self.__connection:
            return factory(transaction=self, **kw)

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
