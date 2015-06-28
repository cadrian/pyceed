class MultiFeed(object):
	"""
	Gather one or more feeds

	No warranty on the order of the entries from each field.
	"""

	def __init__(self, *feeds):
		self._feeds = list(feeds)

	def add_feed(self, feed):
		self._feeds.append(feed)

	def entries(self):
		for feed in self._feeds:
			for entry in feed.entries():
				yield entry

	def update(self):
		for feed in self._feeds:
			feed.update()
