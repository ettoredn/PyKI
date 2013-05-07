__author__ = 'ettore'

import openssl
from bottle import route, view, run, template, request

# SPKAC challenge i.e. certificate request challenge
challenge = "Should be a random generated string"


@route('/')
@view('index')
def index():
    return dict(challenge=challenge)


@route('/generate', method='POST')
def generate():
    type = request.forms.get('type')
    email = request.forms.get('email')
    dns = request.forms.get('dns')
    commonName = request.forms.get('common_name')
    organization = request.forms.get('organization')
    locality = request.forms.get('locality')
    country = request.forms.get('country')

    # DER encoded
    spkac = request.forms.get('key')

    # redirect the user to /show/<certificate hash>
    return openssl.signSPKAC(spkac, type, email=email, DNS=dns, CN=commonName, O=organization, L=locality, C=country)


@route('/hello/<name>')
def hello(name='Guest'):
    return template('Hello {{ name }}', name=name)

run(host='localhost', port='8080', debug=True)
