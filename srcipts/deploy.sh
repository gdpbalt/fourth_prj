#!/bin/bash
#
#
cd /home/ubuntu/control/flask

source /home/ubuntu/control/flask/venv/bin/activate
export FLASK_APP=myapp.py

/efs/var/www/control/flask/venv/bin/flask db current -v

# login: gdpbalt
# project: 
/usr/bin/git pull

# migrate
/efs/var/www/control/flask/venv/bin/flask db upgrade

# install python modules
/efs/var/www/control/flask/venv/bin/pip install -r requirements.txt


# test
/efs/var/www/control/flask/venv/bin/coverage run -m unittest discover

