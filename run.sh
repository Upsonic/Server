#!/bin/bash

mkdir -p /keys

openssl req -x509 -newkey rsa:4096 -keyout /keys/upsonic.private.pem -out /keys/upsonic.origin.pem -days 365 -nodes -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.upsonic.co"

service nginx start 

upsonic_on_prem api --host=0.0.0.0 --port=3000 &

python3 /app/On-Prem/upsonic_on_prem/dash/manage.py makemigrations --noinput
python3 /app/On-Prem/upsonic_on_prem/dash/manage.py migrate --noinput
python3 /app/On-Prem/upsonic_on_prem/dash/manage.py collectstatic --noinput


cd /app/On-Prem/upsonic_on_prem/dash/

echo "from app import models; models.User.objects.create_superuser('$admin_user', 'onprem@upsonic.co', '$admin_pass')" | python3 manage.py shell


gunicorn --bind localhost:3001 dash.wsgi:application