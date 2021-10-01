from control import db


class OtpuskHotelTA(db.Model):
    __tablename__ = 'otpusk_hotel_ta'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    url = db.Column(db.String(255), nullable=False)
    expired = db.Column(db.DateTime, nullable=False, index=True)
    updated = db.Column(db.DateTime, nullable=False,
                        server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class OtpuskHotelTACache(db.Model):
    __tablename__ = 'otpusk_hotel_ta_cache'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    page = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text(1048576), nullable=True)
    expired = db.Column(db.DateTime, nullable=False, index=True)
    updated = db.Column(db.DateTime, nullable=False,
                        server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
