import re

class FeedSort(object):
	"""
	Sort the feed entries according to the given field.
	"""

	def __init__(self, feed, field, reverse=False):
		self._feed = feed
		self._field = field
		self._reverse = reverse

	def entries(self):
		for entry in sorted(
				self._feed.entries(),
				key=lambda e: getattr(e.definition, self._field),
				reverse=self._reverse,
		):
			yield entry

	def update(self):
		self._feed.update()


class FeedTruncate(object):
	"""
	Limit the number of feeds
	"""

	def __init__(self, feed, limit):
		self._feed = feed
		self._limit = limit

	def entries(self):
		count = 0
		for entry in self._feed.entries():
			if count < self._limit:
				yield entry
				count += 1
			else:
				break

	def update(self):
		self._feed.update()


class FeedRegex(object):
	"""
	Filter the feed entries according to the given regex
	"""

	def __init__(self, feed, field, regex, flags=0):
		self._feed = feed
		self._field = field
		self._pattern = re.compile(regex, flags=flags)

	def entries(self):
		for entry in self._feed.entries():
			if self._pattern.fullmatch(getattr(entry.definition, self._field)):
				yield entry

	def update(self):
		self._feed.update()
