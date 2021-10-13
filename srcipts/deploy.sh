#!/bin/bash
#
#
cd /home/ubuntu/control/flask

source /home/ubuntu/control/flask/venv/bin/activate
export FLASK_APP=myapp.py

# check current version
/efs/var/www/control/flask/venv/bin/flask db current -v

# login: gdpbalt
# project: 
/usr/bin/git pull

# install python modules
/efs/var/www/control/flask/venv/bin/pip install -r requirements.txt

# migrate
/efs/var/www/control/flask/venv/bin/flask db upgrade

# test
/efs/var/www/control/flask/venv/bin/coverage run -m unittest discover

