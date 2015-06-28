class MultiFeed(object):
	"""
	Gather one or more feeds
	"""

	def __init__(self):
		self._feeds = {}

	def add_feed(self, feed):
		self._feeds[feed.rowid] = feed

	def entries(self):
		for feed in self._feeds.values():
			for entry in feed.entries():
				yield entry
