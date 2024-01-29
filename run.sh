#!/bin/bash

openssl req -x509 -newkey rsa:4096 -keyout /keys/upsonic.private.pem -out /keys/upsonic.origin.pem -days 365 -nodes -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.upsonic.co"

service nginx start

upsonic_on_prem api --host=0.0.0.0 --port=3000