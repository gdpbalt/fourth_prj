from control import db


class OtpuskHotelTA(db.Model):
    __tablename__ = 'otpusk_hotel_ta'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
