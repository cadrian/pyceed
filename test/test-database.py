#!/usr/bin/env python3

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
