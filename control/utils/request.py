# -*- coding: utf-8 -*-
import json

import requests

from config import config
from control import app
from control.settings import API_URL_PRIMARY, LANGS, API


def get_method_link_prepend(method):
    link = '{}/{}?'.format(API_URL_PRIMARY, method)
    return link


def get_method_link_append(lang=LANGS[0]):
    params = list()
    params.append('{}={}'.format(API['lang_name'], lang))
    params.append('{}={}'.format(API['token_name'], app.config['TOKEN']))
    link = '&'.join(params)
    return link


def get_data_from_request(url):
    try:
        app.logger.debug(f'GET {url}')
        r = requests.get(url)
    except Exception as e:
        msg = f'Network connection error'
        app.logger.error(f"{msg}. {e}")
        return

    if r.status_code != requests.codes.ok:
        msg = f'Network connection error'
        app.logger.error(f'{msg}. Answer={r.status_code}')
        return

    try:
        result = json.loads(r.text)
        return result
    except Exception as e:
        msg = f'Received bad json'
        app.logger.error(f"{msg}. {e}. Response='{r.text}'")
        return
