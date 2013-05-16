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

Generate CRL in PEM format

    openssl ca -config conf/CA/ca-sign.conf -gencrl -out conf/CA/crl/crl.pem

Convert a CRL from PEM to DER format

    openssl crl -in crl.pem -outform DER -out crl.crl

Convert PEM certificate to DER format

    openssl x509 -in cert.pem -inform PEM -out cert.der -outform DER

Create a PKCS#7 bundle form multiple certificates in PEM format

    openssl crl2pkcs7 -nocrl -certfile tmp/cert.pem -certfile conf/CA/certificate.pem -outform der

Convert PEM certificate to PKCS#12 file without private key

    openssl pkcs12 -export -in conf/CA/newcerts/01.pem -nokeys -name "My Cert"