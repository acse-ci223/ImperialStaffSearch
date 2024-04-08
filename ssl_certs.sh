#!/bin/bash
set -e

OPENSSL_INSTALLED=false

if which openssl >/dev/null
then 
  OPENSSL_INSTALLED=true
fi

## certificate parameters
COUNTRY_NAME="UK"
STATE_NAME="London"
LOCALITY_NAME="London"
ORGANIZATION_NAME="ICL"
ORGANIZATIONAL_UNIT_NAME="ICL"
COMMON_NAME="iclstaff.com"
EMAIL_ADDRESS="ci223@ic.ac.uk"

## apache or nginx
SERVER_KEY="key.pem"
SERVER_KEY_PATH="/usr/src/app/certs"
SERVER_CRT="cert.pem"
SERVER_CRT_PATH="/usr/src/app/certs"

OPENSSL_SUBJ_OPTIONS="
Country Name (2 letter code) [AU]:$COUNTRY_NAME
State or Province Name (full name) [Some-State]:$STATE_NAME
Locality Name (eg, city) []:$LOCALITY_NAME
Organization Name (eg, company) [Internet Widgits Pty Ltd]:$ORGANIZATION_NAME
Organizational Unit Name (eg, section) []:$ORGANIZATIONAL_UNIT_NAME
Common Name (e.g. server FQDN or YOUR name) []:$COMMON_NAME
Email Address []:$EMAIL_ADDRESS
"

if [ "$OPENSSL_INSTALLED" = true ]
then 
    echo "generating self signed certificate"
    echo "with these options: "
    echo "$OPENSSL_SUBJ_OPTIONS"
    echo ""

    ## generate self signed certificate
    openssl req \
        -new \
        -newkey rsa:4096 \
        -days 365 \
        -nodes \
        -x509 \
        -subj "/emailAddress=$EMAIL_ADDRESS/C=$COUNTRY_NAME/ST=$STATE_NAME/L=$LOCALITY_NAME/O=$ORGANIZATION_NAME/OU=$ORGANIZATIONAL_UNIT_NAME/CN=$COMMON_NAME" \
        -keyout $SERVER_KEY \
        -out $SERVER_CRT
    
    ## uncomment: move to correct location
    mv -f $SERVER_KEY $SERVER_KEY_PATH/$SERVER_KEY
    mv -f $SERVER_CRT $SERVER_CRT_PATH/$SERVER_CRT
else
    echo "openssl is not installed"
    exit 1
fi

#end