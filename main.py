__author__ = 'ettore'

import openssl
from bottle import install, route, view, run, request, response, template, redirect
from bottle_sqlite import SQLitePlugin

install(SQLitePlugin(dbfile='certificates.db'))

# SPKAC challenge i.e. certificate request challenge
challenge = "Should be a random generated string"


@route('/')
@view('index')
def index():
    return dict(challenge=challenge)


@route('/generate', method='POST')
def generate(db):
    type = request.forms.get('type')
    email = request.forms.get('email')
    dns = request.forms.get('dns')
    commonName = request.forms.get('common_name')
    organization = request.forms.get('organization')
    locality = request.forms.get('locality')
    country = request.forms.get('country')

    # DER encoded
    spkac = request.forms.get('key')

    # Calculate serial
    res = db.execute('SELECT COUNT(*) AS count FROM certificates')
    certSerial = '{:02d}'.format(int(res.fetchone()['count']) + 1, 'utf-8')

    print('Serial: {}'.format(certSerial))

    PEMCert = openssl.signSPKAC(spkac, type, certSerial, email=email, DNS=dns, CN=commonName, O=organization, L=locality, C=country)
    certFingerprint = openssl.x509Fingerprint(PEMCert)
    certHash = openssl.x509SubjectHash(PEMCert)

    # Store into the database
    db.execute('INSERT INTO certificates (serial,fingerprint,subject_hash,certificate) VALUES(?, ?, ?, ?)',
               (certSerial, certFingerprint, certHash, PEMCert))

    # redirect the user to /show/<certificate hash>
    redirect('/show/{}'.format(certSerial))
    # return '<pre>Certificate:\n{}\n\nSubject Hash: {}\nFingerprint: {}'.format(PEMCert, certHash, certFingerprint)


@route('/show/:serial', method='GET')
def show(serial, db):
    if not serial:
        return

    res = db.execute('SELECT * FROM certificates WHERE serial = ?', (serial,))
    certificate = res.fetchone()

    return template('show', certificate=certificate['certificate'])


@route('/pyki.crl')
def showCRL():
    crl = ''

    try:
        crl = openssl.generateCRL()
    except BaseException as e:
        print(e)

    # Set response type to application/pkix-crl
    response.content_type = 'application/pkix-crl'

    return crl


run(host='localhost', port='8080', debug=True)
