import logging

from bottle import Bottle, run, template, request, response, redirect, view

from pyceed.db import Transaction, Filter, Feed
from pyceed.config import connection, host, port

def getApp(root="/"):
	app = Bottle()
	trn = Transaction(connection)

	@app.get(root + 'hello')
	@app.get(root + 'hello/')
	@app.get(root + 'hello/<name>')
	def hello(name="World"):
		return template('<b>Hello {{name}}</b>!', name=name)

	@app.get(root + "config")
	@app.get(root + "config/")
	@view("config")
	def config():
		filters = [f for f in trn.select_all(Filter, insert=False)]
		return dict(
			root=root,
			filters=filters,
		)

	@app.post(root + "config")
	def do_config():
		name = request.forms.get('config_name')
		if name is None or name == "_new":
			name = request.forms.get('config_name_text')
		return redirect(root + "config/" + name)

	@app.get(root + "config/<filtername>")
	@view("config_filter")
	def config_filter(filtername):
		filter = trn.select_unique(Filter, name=filtername)
		if filter.definition is None:
			filter.definition = ""
		return dict(
			root=root,
			filter=filter,
		)

	@app.post(root + "config/<filtername>")
	def config_filter(filtername):
		try:
			definition = request.forms.get("definition") or ""
			filter = trn.select_unique(Filter, name=filtername, definition=definition)
			filter.update()
			for feed in trn.select_all(Feed, insert=False):
				feed.update()
			trn.commit()
		except:
			logging.exception("config_filter failed for filter %s" % (filtername,))
			trn.rollback()
		return redirect(root + "config")

	return app


if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] <%(threadName)s> %(message)s')
	run(getApp("/"), host=host, port=port)
