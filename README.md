Generate CA private key:

    openssl genrsa -out private/cakey.pem 4096

Compute the public key given the private key

    openssl rsa -in private/cakey.pem -pubout

Generate self-signed root CA x.509 certificate

    openssl req -config openssl.conf -new -key private/cakey.pem -x509 -out certificate.pem

Verify certificate with SSL Server purpose

    openssl verify -CAfile conf/CA/certificate.pem -purpose sslserver -issuer_checks -x509_strict conf/CA/newcerts/01.pem

Sign a certificate request in SPKAC format

    openssl ca -config conf/CA/ca-sign.conf -spkac tmp/spkacFile.txt -verbose -extensions sslserver

Start the builtin SSL Server in order to test the certificates

    openssl s_server -cert conf/CA/newcerts/01.pem -key tmp/localhost.pem -CAfile conf/CA/certificate.pem -www

Converts PKCS12 certificate to PEM

    openssl pkcs12 -in tmp/localhost.p12 -out tmp/localhost.pem

Generate CRL in PEM format

    openssl ca -config conf/CA/ca-sign.conf -gencrl -out conf/CA/crl/crl.pem

Convert CRL to PKCS7 format

    openssl crl2pkcs7 -in conf/CA/crl/crl.pem -out conf/CA/crl/crl.pkcs7 -outform DER
