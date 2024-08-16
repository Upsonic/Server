sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install redis git gh python3 python3-pip -y
sudo pip3 install -r requirements.txt
sudo mkdir /db
sudo chown -R redis:redis /db

cd upsonic_on_prem
cd dash
python3 manage.py migrate --noinput
echo "from app import models; models.User.objects.create_superuser('user', 'user@upsonic.co', '123', access_key='123')" | python3 manage.py shell

echo "
admin_pass = 123
admin_key = 123
admin_username = user
debug = True
custom_connection_url = 'http://localhost:3000'
" > .env

cd ..
cd api

echo "
admin_pass = 123
admin_key = 123
admin_username = user
debug = True
custom_connection_url = 'http://localhost:3000'
" > .env