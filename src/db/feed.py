# Feed

class FeedException(Exception):
	pass

class Feed(object):
	def __init__(self, cursor, key=None, url=None)
		cursor.execute("create table if not exists Feed (url, etag)")
		if key is None:
			if url is None:
				raise FeedException("url is needed")
			self.url = url
			cursor.execute("insert into Feed (url) values (?, ?)", (self.__key, url))
			self.__key = cursor.getconnection().last_insert_rowid()
		else:
			self.__key = key
			for row in cursor.execute("select url from Feed where rowid = ?", (self.__key,)):
				self.url = row[0]
		self.__url = self.url

	def __eq__(self, other):
		return self.__type__ == other.__type__ and self.key == other.key

	def commit(self, cursor):
		if self.__url != self.url:
			cursor.execute("update Feed set url = ? where key = ?", (self.url, self.__key))
			self.__url = self.url

	def rollback(self, cursor):
		self.url = self.__url

	def __getattr__(self, name):
		if name == "key":
			return self.__key
		raise AttributeError
