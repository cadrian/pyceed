from bottle import route, run, template

from pyceed.config import connection, host, port

@route('/hello/<name>')
def index(name):
	return template('<b>Hello {{name}}</b>!', name=name)

if __name__ == '__main__':
	run(host=host, port=port)
