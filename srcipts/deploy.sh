#!/bin/bash
#
#
cd /home/ubuntu/control/flask

source /home/ubuntu/control/flask/venv/bin/activate
export FLASK_APP=myapp.py

# check current version
/home/ubuntu/control/flask/venv/bin/flask db current -v

# login: gdpbalt
# project: fourth_prj
/usr/bin/git pull

# install python modules
/home/ubuntu/control/flask/venv/bin/pip install -r requirements.txt

# migrate
/home/ubuntu/control/flask/venv/bin/flask db upgrade

# test
/home/ubuntu/control/flask/venv/bin/coverage run -m unittest discover

