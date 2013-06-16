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
    certs = []

    # Retrieve certificate serials
    res = db.execute('SELECT serial,type,common_name FROM certificates')
    row = res.fetchone()
    while row:
        certs.append(row)
        row = res.fetchone()

    return template('index', challenge=challenge, certs=certs)


@route('/generate', method='POST')
def generate(db):
    type = request.forms.get('type')
    email = request.forms.get('email')
    dns = request.forms.get('dns')
    commonName = request.forms.get('common_name')
    organization = request.forms.get('organization')
    locality = request.forms.get('locality')
    country = request.forms.get('country')

    # PEM encoded
    spkac = request.forms.get('key')

    # Calculate serial
    res = db.execute('SELECT COUNT(*) AS count FROM certificates')
    certSerial = '{:02d}'.format(int(res.fetchone()['count']) + 1, 'utf-8')

    print('Serial: {}'.format(certSerial))

    PEMCertificate = openssl.signSPKAC(spkac, type, certSerial, email=email, DNS=dns, CN=commonName, O=organization,
                                L=locality, C=country)
    certFingerprint = openssl.x509Fingerprint(PEMCertificate)
    certHash = openssl.x509SubjectHash(PEMCertificate)

    # Store into the database
    if type == "sslserver":
        commonName = dns
    elif type == "smime":
        commonName = email
    db.execute(
        'INSERT INTO certificates (serial,fingerprint,subject_hash,type,common_name,certificate)' +
        'VALUES(?, ?, ?, ?, ?, ?)', (certSerial, certFingerprint, certHash, type, commonName, PEMCertificate))

    # Make the browser install the certificate in DER format
    DERCertificate = openssl.PEMtoDER(PEMCertificate)
    response.content_type = 'application/x-x509-user-cert'

    return DERCertificate


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
        # Set MIME header
        response.content_type = 'application/x-pem-file'

        return PEMCertificate
    elif certFormat == "cer":
        DERCertificate = openssl.PEMtoDER(PEMCertificate)

        # Set MIME header
        response.content_type = 'application/pkix-cert'

        return DERCertificate
    elif certFormat == "p7c":
        PKCS7Certificate = openssl.PEMtoPKCS7(PEMCertificate)

        # Set MIME header
        response.content_type = 'application/pkcs7-mime'

        return PKCS7Certificate
    elif certFormat == "p12":
        PKCS12Certificate = openssl.PEMtoPKCS12(PEMCertificate)

        # Set MIME header
        response.content_type = 'application/x-pkcs12'

        return PKCS12Certificate
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
def clearCA(db):
    try:
        if os.path.exists('conf/CA/index.txt.attr'):
            os.remove('conf/CA/index.txt.attr')
        if os.path.exists('conf/CA/index.txt.attr.old'):
            os.remove('conf/CA/index.txt.attr.old')
        if os.path.exists('conf/CA/index.txt.old'):
            os.remove('conf/CA/index.txt.old')
        if os.path.exists('conf/CA/serial.old'):
            os.remove('conf/CA/serial.old')

        for cert in os.listdir('conf/CA/newcerts'):
            if not cert.endswith('.pem'):
                continue

            os.remove('conf/CA/newcerts/{}'.format(cert))

    except FileNotFoundError as e:
        print(e)

    # Clear index file
    indexFile = open('conf/CA/index.txt', 'w')
    indexFile.write('')
    indexFile.close()

    # Clear database
    db.execute('DELETE FROM certificates')

    return 'Done'


run(host='localhost', port='8080', debug=True)
