#!/usr/bin/env sh

set -e

cat > openssl.cnf <<EOF

[req]
x509_extensions = usr_cert

[usr_cert]
1.3.6.1.4.1.45724.2.1.1=ASN1:FORMAT:BITLIST,BITSTRING:2

EOF

# generate key and self-signed certificate
openssl ecparam -genkey -name prime256v1 -out $1/attestation_key.pem
openssl req -new -sha256 -key $1/attestation_key.pem -out $1/csr.csr -subj "/C=US/CN=H2LAB U2F Token"
openssl req -config openssl.cnf -x509 -sha256 -days 3650 -key $1/attestation_key.pem -in $1/csr.csr -out $1/attestation.pem
rm -f openssl.cnf

# convert to der
openssl x509 -outform der -in $1/attestation.pem -out $1/attestation.der
openssl ec -in $1/attestation_key.pem -outform der -out $1/attestation_key.der
