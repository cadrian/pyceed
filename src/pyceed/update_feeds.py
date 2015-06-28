#!/usr/bin/env python3

from pyceed.db import Transaction, Feed

import apsw

import pyceed.config

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
