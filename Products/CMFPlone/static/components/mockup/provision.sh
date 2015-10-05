#!/bin/bash

export LC_ALL="en_US.UTF-8"
DEBIAN_FRONTEND=noninteractive
swapsize=1024

echo $1 > /etc/hostname

grep -q "swapfile" /etc/fstab
if [ $? -ne 0 ]; then
    echo 'swapfile not found. Adding swapfile.'
    fallocate -l ${swapsize}M /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap defaults 0 0' >> /etc/fstab
else
    echo 'swapfile found. No changes made.'
fi

echo "apt-get update & install system packages"
apt-get -qq update
apt-get install -yq npm nodejs-legacy git phantomjs

# echo "Wiring up npm cache"
# npm config get cache

echo "Install local development"
# It would be nice to use npm link but I cannot seem to make it work properly
cd /vagrant
npm install -g

echo 'export LC_ALL="en_US.UTF-8"' >> ~vagrant/.bashrc
echo 'export PATH=/vagrant/node_modules/.bin/:$PATH' >> ~vagrant/.bashrc
echo 'export NODE_PATH=/vagrant/node_modules/' >> ~vagrant/.bashrc

echo "Finished."
echo "Run 'vagrant reload' and after, 'vagrant ssh' to access the machine."
