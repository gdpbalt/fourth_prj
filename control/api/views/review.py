import copy
import datetime
import json
from typing import Optional

from flask import make_response, jsonify, request

from control import app, db
from control.classes.api_otpusk_hotel import MethodHotel
from control.classes.ta_review_parser import TAParse, TAParseExeption
from control.models.api_optusk_hotel_ta import OtpuskHotelTA, OtpuskHotelTACache
from control.settings import API
from control.utils.request import get_method_link_prepend, get_method_link_append

MSG_HOTEL_NOT_FOUND = "Hotel ID not found or wrong"
MSG_GET_REVIEW_FAILED = "Getting review is failed"
STATUS_CODE_OK = 200
STATUS_CODE_FAIL = 421

RETURN_BLOCK = {
    "error": False,
    "message": "",
}

DATE_NOW = datetime.datetime.now()


def get_url_from_otpusk(hotel: int) -> Optional[str]:
    data = db.session.query(OtpuskHotelTA).filter(OtpuskHotelTA.id == hotel,
                                                  DATE_NOW <= OtpuskHotelTA.expired).first()
    if data is not None:
        return data.url

    url = "{}hotelId={}&data=extlinks&{}".format(get_method_link_prepend(method=API['method_hotel']),
                                                 hotel, get_method_link_append())
    method = MethodHotel(link=url, lang_id=0, hotel=hotel)
    method.run()
    if len(method.data.keys()) == 0:
        app.logger.warning("Hotel:{}. Get empty 'rb': value from Otpusk ({})".format(hotel, url))
        return
    return method.data["url"]


def get_data_from_ta(hotel: int, page: int, url: str) -> Optional[dict]:
    result = db.session.query(OtpuskHotelTACache).filter(OtpuskHotelTACache.id == hotel,
                                                         OtpuskHotelTACache.page == page,
                                                         DATE_NOW <= OtpuskHotelTACache.expired).first()
    if result is not None:
        if result.content is None:
            app.logger.warning("Hotel:{}, Page:{}. Tripadvisor. Get empty value from database".format(hotel, page))
            return
        content = json.loads(result.content)
        return content

    ta = TAParse(hotel_id=hotel, url=url, page=page)
    try:
        tripadvisor = ta.run()
    except TAParseExeption as e:
        app.logger.warning("Hotel:{}, Page:{}. Get empty value from tripadvisor ({})".format(hotel, page, url))
        app.logger.error(f"Some error occured ({e})")
        return
    else:
        return tripadvisor.dict(by_alias=True)


def get_input_param(params: dict) -> dict:
    output = dict()
    output["error"] = False

    value = params.get('access_token', None)
    if value is None or value != app.config['TOKEN']:
        output["message"] = 'No found partner!'
        output["error"] = True
        return output

    value = params.get('hotelId', None)
    if value is None:
        output["message"] = 'No found hotel id!'
        output["error"] = True
        return output
    else:
        try:
            output["hotel"] = int(value)
        except ValueError:
            output["message"] = 'No found hotel id. Value is wrong!'
            output["error"] = True
            return output

    value = params.get('page', None)
    if value is None:
        output["page"] = 1
    else:
        try:
            output["page"] = int(value)
        except ValueError:
            output["message"] = 'No found page. Value is wrong!'
            output["error"] = True
            return output

    if output["page"] == 0:
        output["page"] = 1

    return output


def form_error_response(message: str) -> dict:
    data = copy.deepcopy(RETURN_BLOCK)
    data["error"] = True
    data["message"] = message
    data["data"] = None
    return data


@app.route("/api/review")
def get_ta_review():
    keys = get_input_param(params=request.args)
    if keys["error"]:
        output = form_error_response(keys["message"])
        response = make_response(jsonify(output), STATUS_CODE_FAIL)
        return response

    hotel = keys["hotel"]
    page = keys["page"]

    if (url := get_url_from_otpusk(hotel=hotel)) is None:
        output = form_error_response(MSG_HOTEL_NOT_FOUND)
        response = make_response(jsonify(output), STATUS_CODE_FAIL)
        app.logger.warning("Hotel:{}, Page:{}. Otpusk don't have tripadvisor's url".format(hotel, hotel))
        return response

    data_dict = get_data_from_ta(hotel=hotel, page=page, url=url)
    if data_dict is None:
        output = form_error_response(MSG_GET_REVIEW_FAILED)
        response = make_response(jsonify(output), STATUS_CODE_FAIL)
        app.logger.warning("Hotel:{}, Page:{}. Can't parse tripadvisor html".format(hotel, hotel))
        return response

    output = copy.deepcopy(RETURN_BLOCK)
    output["data"] = data_dict
    output["time"] = output["data"]["time"]
    output["updated"] = output["data"]["updated"]
    del output["data"]["time"]
    del output["data"]["updated"]

    response = make_response(jsonify(output), STATUS_CODE_OK)
    return response
