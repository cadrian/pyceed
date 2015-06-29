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
import os

connection = apsw.Connection("dbfile")
cursor = connection.cursor()

cursor.execute("create table test(id, value)")

for id, value in [
	(1, "foo"),
	(2, "bar"),
	(42, "everything")
]:
	cursor.execute("insert into test(id, value) values (:id, :value)", {
		"id": id,
		"value": value,
	})

for row in cursor.execute("select id, value from test order by value"):
	print("%s | %s" % row)

connection.close(True)
os.remove("dbfile")
