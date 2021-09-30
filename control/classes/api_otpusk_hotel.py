import datetime

from sqlalchemy import exc

from control import db, app
from control.classes.api_otpusk import MethodOtpusk
from control.models.api_optusk_hotel_ta import OtpuskHotelTA
from control.settings import TRIPADVISER_GET_URL_FROM_OTPUSK_AFTER_DAYS


class MethodHotel(MethodOtpusk):
    def __init__(self, link, lang_id, hotel):
        super().__init__(link=link, lang_id=lang_id)
        self.hotel_id = hotel

    @staticmethod
    def parse_result(input_data: dict) -> dict:
        response = input_data.get('hotel', dict())
        if not isinstance(response, dict) or len(response.keys()) == 0:
            return dict()

        response = response.get('rb', dict())
        if not isinstance(response, dict) or len(response.keys()) == 0:
            return dict()

        response = response.get('1', dict())
        if not isinstance(response, dict) or len(response.keys()) == 0:
            return dict()

        output = dict()
        response = response.get('url')
        if response is not None:
            output['url'] = response
        return output

    def save_data2dbase(self):
        if len(self.data.keys()) == 0:
            return

        updated = datetime.datetime.now()
        expired = updated + datetime.timedelta(days=TRIPADVISER_GET_URL_FROM_OTPUSK_AFTER_DAYS)

        result: OtpuskHotelTA = OtpuskHotelTA.query.get(self.hotel_id)
        if result is None:
            result = OtpuskHotelTA(id=self.hotel_id, url=self.data["url"], expired=expired, updated=updated)
            db.session.add(result)
        else:
            result.url = self.data["url"]
            result.expired = expired
            result.update = updated

        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            msg = f'Error work with database. {e}'
            app.logger.error(msg)
            raise ConnectionError(msg)
