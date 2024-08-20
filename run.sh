#!/bin/bash

chown -R redis:redis /db
cd /app/Server/
ollama serve &
sleep 30s
python3 ollama_setting.py
ollama create upsonic_local_model -f Modelfile
ollama create nomic-embed-text-upsonic -f Modelfile_2

python3 /app/Server/ssl_setting.py

service nginx start 


cd /app/Server/upsonic_on_prem/api/
python3 main.py --host=0.0.0.0 --port=3000 &

python3 /app/Server/upsonic_on_prem/dash/manage.py makemigrations --noinput
python3 /app/Server/upsonic_on_prem/dash/manage.py migrate --noinput
python3 /app/Server/upsonic_on_prem/dash/manage.py collectstatic --noinput


cd /app/Server/upsonic_on_prem/dash/

echo "from app import models; models.User.objects.create_superuser('$admin_username', 'onprem@upsonic.co', '$admin_pass', access_key='$admin_key')" | python3 manage.py shell


gunicorn --bind localhost:3001 --workers=5 --timeout 0 dash.wsgi:application
