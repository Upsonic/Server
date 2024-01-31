import os

generate_command = 'openssl req -x509 -newkey rsa:4096 -keyout /var/lib/redis/upsonic.private.pem -out /var/lib/redis/upsonic.origin.pem -days 365 -nodes -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.upsonic.co"'

if not os.path.exists("/var/lib/redis/upsonic.private.pem"):
    os.system(generate_command)
