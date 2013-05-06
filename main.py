__author__ = 'ettore'

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
    commonName = request.forms.get('common_name')
    organization = request.forms.get('organization')
    locality = request.forms.get('locality')
    country = request.forms.get('country')

    # DER encoded
    spkac = request.forms.get('key')

    # Generate text file in SPKAC FORMAT as specified in openssl ca
    spkacFile = open('tmp/spkacFile.txt', 'w')
    spkacRequest = 'SPKAC={}\nCN={}\nO={}\nL={}\nC={}'.format(spkac, commonName, organization, locality, country)
    spkacFile.write(spkacRequest)
    spkacFile.close()

    # Sign the request using openssl ca -config openssl/CA/ca-sign.conf -spkac tmp/spkacFile.txt -batch -extensions smime
    # redirect the user to /show/<certificate hash>

    return template("""
    <div>SPKAC: {{ pubKey }}</div>
    """, pubKey=spkac)


@route('/hello/<name>')
def hello(name='Guest'):
    return template('Hello {{ name }}', name=name)

run(host='localhost', port='8080', debug=True)
