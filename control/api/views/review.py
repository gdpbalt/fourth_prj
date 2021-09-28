from flask import make_response

from control import app

MSG_HOTEL_NOT_FOUND = "Hotel ID not found or wrong"
MSG_GET_REVIEW_FAILED = "Getting review is failed"


RETURN_BLOCK = {
    "error": False,
    "data": None,
    "message": "",
}


@app.route("/api/review/<int:hotel>")
@app.route("/api/review/<int:hotel>/<int:page>")
def get_ta_review(hotel: int, page: int = 0):
    status_code = 200
    response = make_response(f"ID: {hotel}, Page: {page}", status_code)
    return response
