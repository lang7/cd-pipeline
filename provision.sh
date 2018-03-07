#!/bin/bash
set -e
#provision.sh
sudo yum -y update
echo "yum update done."
sudo yum install -y python-pip
sudo pip install ansible
sudo wget 'https://s3.eu-west-2.amazonaws.com/dev-jl-ppl-cisreports/playbook.yml'
echo "Running build."
sudo ansible-playbook playbook.yml