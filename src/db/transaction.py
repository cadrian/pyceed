# Transaction: just a central point of control for commit / rollback

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
		objs[obj.key] = obj
		return obj

	def create(self, factory, **kw):
		return self.__update_map(factory(cursor=this.cursor, key=None, **kw))

	def select(self, factory, key, **kw):
		self.__update_map(factory(cursor=this.cursor, key=key, **kw))

	def commit(self):
		for obj in this.__objects:
			obj.commit(this.__cursor)

	def rollback(self):
		for obj in this.__objects:
			obj.rollback(this.__cursor)
