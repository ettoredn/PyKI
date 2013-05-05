Generate CA private key:

    openssl genrsa -out private/cakey.pem 4096

Generate root CA self-signed certificate:

Compute the public key given the private key

    openssl rsa -in private/cakey.pem -pubout

Generate self-signed root CA x.509 certificate

    openssl req -config openssl.conf -new -key private/cakey.pem -x509 -out certificate.pem
