from subprocess import check_output, Popen, CalledProcessError, PIPE
import os

# TODO Move to configuration file
__OpenSSLBin = '/usr/bin/openssl'
__OpenSSLConfig = 'conf/CA/ca-sign.conf'
__x509Extensions = {
    'sslserver': """
        basicConstraints = critical, CA:FALSE
        extendedKeyUsage = critical, serverAuth, clientAuth
        subjectAltName = DNS:{0},DNS:www.{0}
        crlDistributionPoints = URI:http://pyki.ettoredelnegro.me/pyki.crl
        authorityInfoAccess = caIssuers;URI:http://pyki.ettoredelnegro.me/pyki.crt
    """,
    'smime': """
        basicConstraints = CA:FALSE
        extendedKeyUsage = critical, emailProtection
        subjectAltName = email:{0}
        crlDistributionPoints = URI:http://pyki.ettoredelnegro.me/pyki.crl
        authorityInfoAccess = caIssuers;URI:http://pyki.ettoredelnegro.me/pyki.crt
    """,
    'codesign': """
        basicConstraints = CA:FALSE
        extendedKeyUsage = critical, codeSigning
        crlDistributionPoints = URI:http://pyki.ettoredelnegro.me/pyki.crl
        authorityInfoAccess = caIssuers;URI:http://pyki.ettoredelnegro.me/pyki.crt
    """
}


def signSPKAC(SPKAC, certificateType, serial, email=None, DNS=None, CN=None, O=None, L=None, C=None):
    # SSL Server
    if certificateType == 'sslserver':
        if not DNS:
            raise Exception('DNS cannot be null when requesting an SSL server certificate')
            # Force CN = DNS
        CN = DNS

    # S/MIME
    elif certificateType == 'smime':
        if not email:
            raise Exception('email cannot be null when requesting an S/MIME certificate')
            # Force CN = email
        CN = email

    # Some browsers e.g. Mozilla add newlines
    SPKAC = SPKAC.replace("\n", "")
    SPKAC = SPKAC.replace("\r", "")

    # Generate SPKAC text file
    spkacFile = open('tmp/spkac.txt', 'w')
    spkacRequest = 'SPKAC={}\nCN={}\nO={}\nL={}\nC={}'.format(SPKAC, CN, O, L, C)
    spkacFile.write(spkacRequest)
    spkacFile.close()

    # Generate extensions file
    extFile = open('tmp/extensions.conf', 'w')
    extFile.write(__x509Extensions[certificateType].format(CN))
    extFile.close()

    # Write serial
    serialFile = open('conf/CA/serial', 'w')
    serialFile.write(serial + '\n')
    serialFile.close()

    # Sign the request
    try:
        check_output([__OpenSSLBin, 'ca',
                      '-config', __OpenSSLConfig,
                      '-spkac', 'tmp/spkac.txt',
                      '-batch',
                      '-extfile', 'tmp/extensions.conf'])
    except CalledProcessError as e:
        print(e.output)
        raise e

    # Extract certificate from PEM file
    certFile = open('conf/CA/newcerts/' + serial + '.pem', 'r')
    lines = certFile.readlines()
    certFile.close()
    PEMCert = ''
    beginCert = False
    for line in lines:
        if line == '-----BEGIN CERTIFICATE-----\n':
            beginCert = True
        if beginCert:
            PEMCert += line

    return PEMCert


def x509SubjectHash(PEMCert):
    # Converts the PEM certificate string into a byte sequence
    PEMCert = bytes(PEMCert, 'utf-8')

    try:
        proc = Popen([__OpenSSLBin, 'x509',
                      '-subject_hash',
                      '-noout'],
                     stdin=PIPE, stdout=PIPE)

        # Returns a tuple (stdoutdata, stderrdata)
        output = proc.communicate(input=PEMCert)[0]
        certHash = str(output, 'utf-8')
    except CalledProcessError as e:
        print(e.output)
        raise e

    # Check return code
    if proc.returncode != 0:
        raise Exception("Error executing OpenSSL")

    return certHash


def x509Fingerprint(PEMCert):
    # Converts the PEM certificate string into a byte sequence
    PEMCert = bytes(PEMCert, 'utf-8')

    try:
        proc = Popen([__OpenSSLBin, 'x509',
                      '-fingerprint',
                      '-noout'],
                     stdin=PIPE, stdout=PIPE)

        # Returns a tuple (stdoutdata, stderrdata)
        output = proc.communicate(input=PEMCert)[0]
        certFingerprint = str(output, 'utf-8')
    except CalledProcessError as e:
        print(e.output)
        raise e

    # Check return code
    if proc.returncode != 0:
        raise Exception("Error executing OpenSSL")

    return certFingerprint


# Returns CRL in DER format
def generateCRL():
    try:
        # Generate CRL in PEM format
        check_output([__OpenSSLBin, 'ca',
                      '-config', __OpenSSLConfig,
                      '-gencrl',
                      '-out',
                      'conf/CA/crl/crl.pem'])

        # Convert to DER format
        crl = check_output([__OpenSSLBin, 'crl',
                      '-in',
                      'conf/CA/crl/crl.pem',
                      '-outform',
                      'DER'])
    except CalledProcessError as e:
        print(e.output)
        raise e

    # Binary string
    return crl


# Convert a x509 certificate from PEM to DER format
def PEMtoDER(PEMCert):
    PEMCert = bytes(PEMCert, 'utf-8')

    try:
        proc = Popen([__OpenSSLBin, 'x509',
                      '-inform',
                      'PEM',
                      '-outform',
                      'DER'],
                     stdin=PIPE, stdout=PIPE)

        # Returns a tuple (stdoutdata, stderrdata)
        output, stderr = proc.communicate(input=PEMCert)
        return output
    except CalledProcessError as e:
        print(e.output)
        raise e


# Create a PKCS#7 bundle from a x509 certificate in PEM format
def PEMtoPKCS7(PEMCert):
    # crl2pkcs7 doesn't support certfiles from stdin
    certFile = open('tmp/cert.pem', 'w')
    certFile.write(PEMCert)
    certFile.close()

    if not os.path.exists('conf/CA/certificate.pem'):
        raise Exception('Unable to find CA certificate in conf/CA/certificate.pem')

    # Create PKCS7 including CA certificate
    try:
        pkcs7 = check_output([__OpenSSLBin, 'crl2pkcs7',
              '-nocrl',
              # '-certfile',
              # 'conf/CA/certificate.pem',
              '-certfile',
              'tmp/cert.pem',
              '-outform',
              'DER'])
    except CalledProcessError as e:
        print(e.output)
        raise e

    return pkcs7


# Created a PKCS#12 bundle from a x509 certificate in PEM format
def PEMtoPKCS12(PEMCert):
    PEMCert = bytes(PEMCert, 'utf-8')

    try:
        # openssl pkcs12 -export -in conf/CA/newcerts/01.pem -nokeys -name "My Cert"
        proc = Popen([__OpenSSLBin, 'pkcs12',
                      '-export',
                      '-nokeys',
                      '-passout',
                      'pass:pyki',
                      '-name',
                      'Pretty Name'],
                     stdin=PIPE, stdout=PIPE)

        # Returns a tuple (stdoutdata, stderrdata)
        output, stderr = proc.communicate(input=PEMCert)
        return output
    except CalledProcessError as e:
        print(e.output)
        raise e