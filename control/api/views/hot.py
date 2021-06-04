from flask import jsonify, request, make_response

from control import app, cache, LANGS
from control.classes.mk_hot_block import HotBlock
from control.classes.mk_hot_tour import TourBlock
from control.models import Showcase, Tour
from control.settings import MYAPI_HEADERS

ERROR_BLOCK = {
    "error": True,
    "data": None,
    "message": "",
    "api_version": "1",
    "time": 0
}


def form_response(endpoint, params):
    input_token = params.get('access_token', None)
    if input_token is None or input_token != app.config['TOKEN']:
        ERROR_BLOCK['message'] = 'No found partner!'
        return ERROR_BLOCK

    input_id_1 = params.get('blockId', None)
    if input_id_1 is not None:
        input_id = input_id_1
    else:
        ERROR_BLOCK['message'] = 'No found block!'
        return ERROR_BLOCK

    input_lang = params.get('lang', None)
    if input_id is None or input_lang not in LANGS:
        input_lang = 0
    else:
        input_lang = LANGS.index(input_lang)

    if endpoint == 'hot_block':
        data = Showcase.query.get(input_id)
        if data is None:
            ERROR_BLOCK['message'] = f'No found block {input_id}'
            return ERROR_BLOCK
        return get_hot_block(index=data.id, lang_id=input_lang)

    else:
        data = Tour.query.get(input_id)
        if data is None or data.active is False:
            ERROR_BLOCK['message'] = f'No found block {input_id}'
            return ERROR_BLOCK
        return get_hot_tour(index=data.id, lang_id=input_lang)


@cache.memoize()
def get_hot_block(index, lang_id):
    showcase = HotBlock(index, lang_id)
    showcase.run()
    return showcase.response


@cache.memoize()
def get_hot_tour(index, lang_id):
    tour = TourBlock(index, lang_id)
    tour.run()
    return tour.response


@app.route("/hotBlock")
@app.route("/hotblock")
def hot_block():
    array = form_response(endpoint=request.endpoint, params=request.args)
    response = make_response(jsonify(array), MYAPI_HEADERS)
    return response


@app.route("/hotTour")
@app.route("/hottour")
def hot_tour():
    array = form_response(endpoint=request.endpoint, params=request.args)
    response = make_response(jsonify(array), MYAPI_HEADERS)
    return response
