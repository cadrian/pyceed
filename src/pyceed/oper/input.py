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
