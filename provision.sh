#!/bin/bash
set -e
#provision.sh
sudo apt-get -y update
echo "apt-get update done."
sudo apt-get install -y python-dev python-pip
sudo pip install ansible
sudo timedatectl set-timezone Europe/Istanbul
sudo localectl set-locale LANG=en_US.utf8
sudo wget 'https://s3.eu-west-2.amazonaws.com/dev-jl-ppl-cisreports/playbook.yml'
echo "Running build."
sudo ansible-playbook playbook.yml