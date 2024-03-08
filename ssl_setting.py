import os
import subprocess

generate_command = 'openssl req -x509 -newkey rsa:4096 -keyout /db/upsonic.private.pem -out /db/upsonic.origin.pem -days 365 -nodes -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.upsonic.co"'

if not os.path.exists("/db/upsonic.private.pem"):
    os.system(generate_command)
