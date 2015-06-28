class MultiFeed(object):
	"""
	Gather one or more feeds

	No warranty on the order of the entries from each field.
	"""

	def __init__(self):
		self._feeds = {}

	def add_feed(self, feed):
		self._feeds[feed.rowid] = feed

	def entries(self):
		for feed in self._feeds.values():
			for entry in feed.entries():
				yield entry
