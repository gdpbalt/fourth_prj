from datetime import datetime, timedelta

from control import db, app
from control.models.api_optusk_hotel_ta import OtpuskHotelTA, OtpuskHotelTACache


def clean_old_data():
    date_remove = datetime.now()

    app.logger.info("Clear old data from table 'otpusk_hotel_ta'")
    db.session.query(OtpuskHotelTA).filter(date_remove > OtpuskHotelTA.expired).delete()
    db.session.commit()

    app.logger.info("Clear old data from table 'otpusk_hotel_ta_cache'")
    db.session.query(OtpuskHotelTACache).filter(date_remove > OtpuskHotelTACache.expired).delete()
    db.session.commit()
