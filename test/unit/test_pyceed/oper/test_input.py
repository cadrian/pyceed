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

import unittest
from mockito import mock, when, verify, verifyNoMoreInteractions, inorder
from pyceed.oper import MultiFeed


class TestMultiFeed(unittest.TestCase):
	"""
	Test MultiFeed
	"""

	def test_entries(self):
		def iterx():
			yield 'foo'
			yield 'bar'
		x = mock()
		x.entries = iterx
		x.rowid = 1

		def itery():
			yield 'baz'
			yield 'zip'
		y = mock()
		y.entries = itery
		y.rowid = 2

		multi = MultiFeed()
		multi.add_feed(x)
		multi.add_feed(y)

		entries = [entry for entry in multi.entries()]
		self.assertEqual(["bar", "baz", "foo", "zip"], sorted(entries))


if __name__ == '__main__':
	unittest.main()
