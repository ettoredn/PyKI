__author__ = 'ettore'

import openssl
import os
from bottle import install, route, run, request, response, jinja2_template as template, redirect
from bottle_sqlite import SQLitePlugin

install(SQLitePlugin(dbfile='certificates.db'))

# SPKAC challenge i.e. certificate request challenge
challenge = "Should be a random generated string"


@route('/')
def index(db):
    serials = []

    # Retrieve certificate serials
    res = db.execute('SELECT serial FROM certificates')
    row = res.fetchone()
    while row:
        serials.append(row[0])
        row = res.fetchone()

    return template('index', challenge=challenge, serials=serials)


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

    PEMCert = openssl.signSPKAC(spkac, type, certSerial, email=email, DNS=dns, CN=commonName, O=organization,
                                L=locality, C=country)
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

    return template('show', certificate=certificate['certificate'], serial=serial)


@route('/download/:serial')
def download(serial, db):
    # Split serial and extension/format
    serial, certFormat = os.path.splitext(serial)
    # Strip point
    certFormat = certFormat.lstrip('.')

    res = db.execute('SELECT * FROM certificates WHERE serial = ?', (serial,))
    row = res.fetchone()
    PEMCertificate = row['certificate']

    # http://pki-tutorial.readthedocs.org/en/latest/mime.html
    if certFormat == "pem":
        response.content_type = 'application/x-pem-file'

        return PEMCertificate
    elif certFormat == "cer":
        response.content_type = 'application/pkix-cert'

        # TODO Convert to DER
        raise Exception('Not implemented')
    elif certFormat == "p7c":
        response.content_type = 'application/pkcs7-mime'

        # TODO Convert to PKCS7
        raise Exception('Not implemented')
    else:
        raise Exception('Unknown certificate type {}'.format(certFormat))


@route('/pyki.crl')
def showCRL():
    crl = ''
    try:
        crl = openssl.generateCRL()
    except BaseException as e:
        print(e)

    # http://www.rfc-editor.org/rfc/rfc2585.txt
    response.content_type = 'application/pkix-crl'

    return crl


@route('/clear')
def clearCA():
    # TODO Clear all certificates, index files, etc
    return None


run(host='localhost', port='8080', debug=True)
