#!/bin/sh

cd /home/ubuntu/control/flask

# --countries  Sync otpusk.countries with dbase
# --from       Sync otpusk.from_cities with dbase
# --operators  Sync otpusk.operators with dbase
# --cities     Sync otpusk.cities with dbase
# --ports      Sync otpusk.ports with dbase

/home/ubuntu/control/flask/venv/bin/python3 /home/ubuntu/control/flask/sync_otpusk_and_local.py --countries

/home/ubuntu/control/flask/venv/bin/python3 /home/ubuntu/control/flask/sync_otpusk_and_local.py --from

/home/ubuntu/control/flask/venv/bin/python3 /home/ubuntu/control/flask/sync_otpusk_and_local.py --operators

/home/ubuntu/control/flask/venv/bin/python3 /home/ubuntu/control/flask/sync_otpusk_and_local.py --cities

/home/ubuntu/control/flask/venv/bin/python3 /home/ubuntu/control/flask/sync_otpusk_and_local.py --ports

