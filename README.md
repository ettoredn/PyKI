Generate CA private key:

    openssl genrsa -out private/cakey.pem 4096

Compute the public key given the private key

    openssl rsa -in private/cakey.pem -pubout

Generate self-signed root CA x.509 certificate

    openssl req -config openssl.conf -new -key private/cakey.pem -x509 -out certificate.pem

openssl verify -CAfile openssl/CA/certificate.pem -purpose sslserver -issuer_checks -x509_strict openssl/CA/newcerts/01.pem
openssl ca -config openssl/CA/ca-sign.conf -spkac tmp/spkacFile.txt -verbose -extensions sslserver
openssl s_server -cert openssl/CA/newcerts/01.pem -key tmp/localhost.pem -CAfile openssl/CA/certificate.pem -www
