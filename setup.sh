#!/bin/bash
# Tested on Ubuntu 16.04.2
# Perform a system update first
echo "[*] Updating the Ubuntu system"
apt update
apt upgrade -y

# Install requried packages
echo "[*] Installing the required packages"
apt install pwgen whois python-pip openssh-server apache2 libapache2-mod-wsgi curl libapache2-modsecurity2 -y

# Create pull user, groups and directories
echo "[*] Creating the SFTP directory"
mkdir -p /opt/automated-pull

echo "[*] Creating the automated-pull user"
newpass=$(pwgen 25 1)
encpass=$(mkpasswd -m sha-512 $newpass)
useradd -m pull-service -p $encpass
chown pull-service /opt/automated-pull

# download api files
wget -O /opt/automated-pull/api.py -q https://raw.githubusercontent.com/OneLogicalMyth/automated-pull/master/api.py
wget -O /opt/automated-pull/blacklist.py -q https://raw.githubusercontent.com/OneLogicalMyth/automated-pull/master/blacklist.py
wget -O /opt/automated-pull/slack.py -q https://raw.githubusercontent.com/OneLogicalMyth/automated-pull/master/slack.py
wget -O /opt/automated-pull/database.py -q https://raw.githubusercontent.com/OneLogicalMyth/automated-pull/master/database.py
wget -O /opt/automated-pull/config.json -q https://raw.githubusercontent.com/OneLogicalMyth/automated-pull/master/config.json
wget -O /opt/automated-pull/api.wsgi -q https://raw.githubusercontent.com/OneLogicalMyth/automated-pull/master/api.wsgi
wget -O /etc/apache2/sites-available/api.conf -q https://raw.githubusercontent.com/OneLogicalMyth/automated-pull/master/api.conf

# secure the config file
chmod 460 /opt/automated-pull/config.json
chown pull-service /opt/automated-pull/config.json

# Configure sudo access for the automated-pull user
echo "[*] Adding sftp sudo file to allow some root access for the api"
echo "pull-service ALL=(ALL) NOPASSWD:/bin/systemctl restart monkey-bot.service" > /etc/sudoers.d/automated-pull
echo "pull-service ALL=(ALL) NOPASSWD:/usr/bin/git pull" >> /etc/sudoers.d/automated-pull
chmod 440 /etc/sudoers.d/automated-pull

# Configure pip, requests and Flask
echo "[*] Upgrading pip"
pip install --upgrade pip
echo "[*] Installing flask"
hash -d pip
pip install Flask
pip install requests

# Add localhost entry for the site, this can be changed to anything later...
printf "\n127.0.0.1 pull-service.local\n" >> /etc/hosts

# secure and tune apache a little
a2dissite 000-default.conf
a2dismod status auth_basic authn_core authn_file authz_host authz_user autoindex -f
mv /etc/modsecurity/modsecurity.conf{-recommended,}
sed -i 's/SecRuleEngine DetectionOnly/SecRuleEngine On/' /etc/modsecurity/modsecurity.conf
printf '\nServerSignature Off\nServerTokens Prod\n' >> /etc/apache2/apache2.conf

# Enabling site and restarting apache2
a2ensite api.conf
service apache2 reload

# Output username and password
echo "[*] Setup complete"
echo ""
echo "[Credentials]"
echo "Username: pull-service"
echo "Password: $newpass"
echo ""
echo "[READY]"
echo ""
echo "Now update the config.json and restart the apache2 service."
