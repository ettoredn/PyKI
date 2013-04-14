__author__ = 'ettore'

from bottle import route, run, template

@route('/')
@route('/hello/<name>')
def hello(name='Guest'):
    return template('Hello {{ name }}', name=name)

run(host='localhost', port='8080', debug=True)
