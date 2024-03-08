import os
import requests
import subprocess
from os import getenv

# Checks if there is an active internet connection
# Returns True if connected, False otherwise
def is_internet_on():
    try:
        response = requests.get("http://www.google.com")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Installs Let's Encrypt (Certbot) if not already installed
# Designed for Ubuntu systems
def install_letsencrypt():
    try:
        # Update system repositories
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        # Install Certbot
        subprocess.run(["sudo", "apt-get", "install", "-y", "certbot"], check=True)
    except subprocess.SubprocessError as e:
        print(f"Error installing Certbot: {e}")

ssl_cert_path = "/db/upsonic.origin.pem"
ssl_key_path = "/db/upsonic.private.pem"

domain_name = getenv("DOMAIN_NAME", "www.upsonic.co") if is_internet_on() else "www.upsonic.co"  # Domain name for certificate generation

if is_internet_on():
    install_letsencrypt()
    # Generate SSL certificates using Let's Encrypt
    try:
        subprocess.run(["sudo", "certbot", "certonly", "--standalone", "-d", domain_name], check=True)
        # Adjust paths after successful generation
        ssl_cert_path = "/etc/letsencrypt/live/" + domain_name + "/fullchain.pem"
        ssl_key_path = "/etc/letsencrypt/live/" + domain_name + "/privkey.pem"
    except subprocess.SubprocessError as e:
        print(f"Error generating Let's Encrypt certificates: {e}")
else:
    generate_command = 'openssl req -x509 -newkey rsa:4096 -keyout ' + ssl_key_path + ' -out ' + ssl_cert_path + ' -days 365 -nodes -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=' + domain_name + '"'
    if not os.path.exists(ssl_key_path):
        raise RuntimeError("Failed to generate self-signed certificate.")  # Improved error handling
    os.system(generate_command)
