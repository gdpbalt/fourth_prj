from typing import Optional

from flask import make_response

from control import app
from control.classes.api_otpusk_hotel import MethodHotel
from control.settings import API
from control.utils.request import get_method_link_prepend, get_method_link_append

MSG_HOTEL_NOT_FOUND = "Hotel ID not found or wrong"
MSG_GET_REVIEW_FAILED = "Getting review is failed"

RETURN_BLOCK = {
    "error": False,
    "data": None,
    "message": "",
}


def get_url_from_otpusk(hotel: int) -> Optional[str]:
    url = "{}hotelId={}&data=extlinks&{}".format(get_method_link_prepend(method=API['method_hotel']),
                                                 hotel, get_method_link_append())
    method = MethodHotel(link=url, lang_id=0)
    method.run()
    if len(method.data.keys()) == 0:
        return
    return method.data["url"]


@app.route("/api/review/<int:hotel>")
@app.route("/api/review/<int:hotel>/<int:page>")
def get_ta_review(hotel: int, page: int = 0):
    url = get_url_from_otpusk(hotel=hotel)

    response = make_response(f"ID: {hotel}, Page: {page}, URL: {url}", 200)
    return response
