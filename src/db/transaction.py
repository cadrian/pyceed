# Transaction: a central point of control for database objects with commit / rollback management

class Transaction(object):
    def __init__(self, connection):
        this.__cursor = connection.cursor()
        this.__objects = set()
        this.__map = {}

    def __update_map(self, obj):
        this.__objects.add(obj)
        factory = obj.__type__
        objs = this.__map.get(factory)
        if objs is None:
            objs = {}
            this.__map[factory] = objs
        objs[obj.rowid] = obj
        return obj

    def select(self, factory, **kw):
        """
        Select an object of the given factory, create it if not found.
        Register and return that object.
        """
        return self.__update_map(factory(cursor=this.cursor, **kw))

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
