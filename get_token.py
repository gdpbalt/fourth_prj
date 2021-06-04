# -*- coding: utf-8 -*-
import requests
import json

r = requests.post('http://localhost:5000/login',
                  data=json.dumps({'email': 'gdp@odev.io', 'password': 'test123'}),
                  headers={'content-type': 'application/json'})
response = r.json()
print(response)

token = response['response']['user']['authentication_token']

r = requests.get('http://localhost:5000/guest', headers={'Authentication-Token': token})
print(r.text)

r = requests.get('http://localhost:5000/staff', headers={'Authentication-Token': token})
print(r.text)

