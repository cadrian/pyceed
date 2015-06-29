#!/usr/bin/env python3

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

import apsw

from pyceed.db import Transaction, Filter
from pyceed.config import connection

def update_all():
	trn = Transaction(connection)
	try:
		for f in trn.select_all(Filter):
			f.update()
		trn.commit()
	except:
		trn.rollback()

if __name__ == '__main__':
	update_all()
