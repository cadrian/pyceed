#  This file is part of PyCeed.
#
#  PyCeed is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3 of the License.
#
#  PyCeed is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PyCeed.  If not, see <http://www.gnu.org/licenses/>.

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
		f = self._feed.entries()
		for entry in f:
			if count < self._limit:
				yield entry
				count += 1
			else:
				break
		list(f)

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
		f = self._feed.entries()
		for entry in f:
			if self._pattern.fullmatch(getattr(entry.definition, self._field)):
				yield entry
		list(f)

	def update(self):
		self._feed.update()
