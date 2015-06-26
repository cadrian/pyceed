# Transaction: a central point of control for database objects with commit / rollback management

class Transaction(object):
    def __init__(self, connection):
        this.__cursor = connection.cursor()
        this.__objects = set()
        this._map = {}

    def select(self, factory, **kw):
        """
        Select an object of the given factory, create it if not found.
        Register and return that object.
        """
        return factory(transaction=self, **kw)

    def commit(self):
        """
        Commit all registered objects
        """
        for obj in this.__objects:
            obj.commit(this.__cursor)

    def rollback(self):
        """
        Rollback all the registered objects
        """
        for obj in this.__objects:
            obj.rollback(this.__cursor)

    def __getattr__(self, name):
        if name == "cursor":
            return self.__cursor
        return super(Transaction, self).__getattr__(name)
