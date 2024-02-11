#!/bin/bash

python3 /app/On-Prem/ssl_setting.py

service nginx start 


cd /app/On-Prem/upsonic_on_prem/dash/
python3 main.py --host=0.0.0.0 --port=3000 &

python3 /app/On-Prem/upsonic_on_prem/dash/manage.py makemigrations --noinput
python3 /app/On-Prem/upsonic_on_prem/dash/manage.py migrate --noinput
python3 /app/On-Prem/upsonic_on_prem/dash/manage.py collectstatic --noinput


cd /app/On-Prem/upsonic_on_prem/dash/

echo "from app import models; models.User.objects.create_superuser('$admin_username', 'onprem@upsonic.co', '$admin_pass')" | python3 manage.py shell


gunicorn --bind localhost:3001 dash.wsgi:application
