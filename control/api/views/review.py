import copy
import datetime
from typing import Optional

from flask import make_response, jsonify

from control import app, db, cache
from control.classes.api_otpusk_hotel import MethodHotel
from control.classes.ta_review_parser import TAParse, TAParseExeption
from control.models.api_optusk_hotel_ta import OtpuskHotelTA
from control.settings import API
from control.utils.request import get_method_link_prepend, get_method_link_append

MSG_HOTEL_NOT_FOUND = "Hotel ID not found or wrong"
MSG_GET_REVIEW_FAILED = "Getting review is failed"
REPEATE_GET_TRIPADVISOR_URL_AFTER_DAYS = 30

RETURN_BLOCK = {
    "error": False,
    "message": "",
}


def get_url_from_otpusk(hotel: int) -> Optional[str]:
    # expire = datetime.datetime.now() - datetime.timedelta(days=REPEATE_GET_TRIPADVISOR_URL_AFTER_DAYS)
    # data = db.session.query(OtpuskHotelTA).filter(OtpuskHotelTA.id == hotel, OtpuskHotelTA.updated >= expire).first()
    # if data is not None:
    #     return data.url

    url = "{}hotelId={}&data=extlinks&{}".format(get_method_link_prepend(method=API['method_hotel']),
                                                 hotel, get_method_link_append())
    method = MethodHotel(link=url, lang_id=0, hotel=hotel)
    method.run()
    if len(method.data.keys()) == 0:
        return
    return method.data["url"]


@app.route("/api/review/<int:hotel>")
@app.route("/api/review/<int:hotel>/<int:page>")
@cache.memoize(timeout=60*60)
def get_ta_review(hotel: int, page: int = 0):
    return_data = copy.deepcopy(RETURN_BLOCK)
    return_error = False
    if (url := get_url_from_otpusk(hotel=hotel)) is None:
        return_error = True
        return_data["message"] = MSG_HOTEL_NOT_FOUND

    else:
        ta = TAParse(url=url, page=page)
        try:
            tripadvisor = ta.run()
        except TAParseExeption:
            return_error = True
            return_data["message"] = MSG_GET_REVIEW_FAILED
        else:
            return_data["data"] = tripadvisor.dict()

    if return_error:
        return_data["error"] = True
        status_code = 400
        return_data["data"] = None
    else:
        return_data["error"] = False
        status_code = 200
        return_data["time"] = return_data["data"]["time"]
        del return_data["data"]["time"]

    response = make_response(jsonify(return_data), status_code)
    return response
