sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install redis git gh python3 python3-pip -y
sudo pip3 install -r requirements.txt
sudo mkdir /db
chown -R redis:redis /db
