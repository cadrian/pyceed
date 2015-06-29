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

import logging

from bottle import Bottle, run, template, request, response, redirect, view
from feedgen.feed import FeedGenerator

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
		filters = list(trn.select_all(Filter, insert=False))
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
			fil = trn.select_unique(Filter, name=filtername)
			fil.definition = request.forms.get("definition") or ""
			fil.title = request.forms.get("title") or ""
			fil.subtitle = request.forms.get("subtitle") or ""
			fil.update()
			trn.commit()
		except:
			logging.exception("config_filter failed for filter %s" % (filtername,))
			trn.rollback()
		return redirect(root + "config")

	@app.get(root + "feed/<type:re:(atom|rss)>/<filtername>")
	def serve_filter(type, filtername):
		try:
			fil = trn.select_unique(Filter, name=filtername, insert=False)
		except:
			logging.exception("serve_filter failed for filter %s" % (filtername,))
			raise

		out_feed = FeedGenerator()
		out_feed.title(fil.title)
		out_feed.subtitle(fil.subtitle)
		out_feed.id(filtername)

		for entry in fil.entries():
			d = entry.definition

			out_entry = out_feed.add_entry()
			out_entry.title(d.title)
			out_entry.published(d.published)
			out_entry.updated(d.updated)
			out_entry.id(d.id)
			out_entry.summary(d.summary)
			for c in getattr(d, "content", []):
				out_entry.content(content=c.value, type=c.type) #, src=c.base
			for l in getattr(d, "links", []):
				out_entry.link(link=l)

		if type == "atom":
			response.content_type = "application/atom+xml"
			return out_feed.atom_str()
		else:
			response.content_type = "application/rss+xml"
			return out_feed.rss_str()

	return app


if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] <%(threadName)s> %(message)s')
	run(getApp("/"), host=host, port=port)
