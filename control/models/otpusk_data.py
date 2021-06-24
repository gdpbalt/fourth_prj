from control import db


class OtpuskCoutries(db.Model):
    __tablename__ = 'otpusk_countris'
    __table_args__ = (db.UniqueConstraint('otpusk_id', 'lang', name='_otpusk_id_lang_uc'),)

    id = db.Column(db.Integer, primary_key=True)
    otpusk_id = db.Column(db.Integer, nullable=False)
    lang = db.Column(db.Integer, db.ForeignKey('lang.id'), nullable=False)

    name = db.Column(db.String(255), nullable=False)


class OtpuskFromCities(db.Model):
    __tablename__ = 'otpusk_from_cities'
    __table_args__ = (db.UniqueConstraint('otpusk_id', 'lang', name='_otpusk_id_lang_uc'),)

    id = db.Column(db.Integer, primary_key=True)
    otpusk_id = db.Column(db.Integer, nullable=False)
    lang = db.Column(db.Integer, db.ForeignKey('lang.id'), nullable=False)

    name = db.Column(db.String(255), nullable=False)
    rel = db.Column(db.String(255), nullable=False)


class OtpuskCities(db.Model):
    __tablename__ = 'otpusk_cities'
    __table_args__ = (db.UniqueConstraint('otpusk_id', 'lang', name='_otpusk_id_lang_uc'),)

    id = db.Column(db.Integer, primary_key=True)
    otpusk_id = db.Column(db.Integer, nullable=False)
    lang = db.Column(db.Integer, db.ForeignKey('lang.id'), nullable=False)

    name = db.Column(db.String(255), nullable=False)
    country = db.Column(db.Integer, nullable=False)

    update = db.Column(db.DateTime, nullable=False,
                       server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class OtpuskOperators(db.Model):
    __tablename__ = 'otpusk_operators'
    __table_args__ = (db.UniqueConstraint('otpusk_id', 'lang', name='_otpusk_id_lang_uc'),)

    id = db.Column(db.Integer, primary_key=True)
    otpusk_id = db.Column(db.Integer, nullable=False)
    lang = db.Column(db.Integer, db.ForeignKey('lang.id'), nullable=False)

    name = db.Column(db.String(255), nullable=False)


class OtpuskPorts(db.Model):
    __tablename__ = 'otpusk_ports'
    __table_args__ = (db.UniqueConstraint('otpusk_id', 'lang', name='_otpusk_id_lang_uc'),
                      db.UniqueConstraint('iata', 'lang', name='_otpusk_iata_lang_uc'),)

    id = db.Column(db.Integer, primary_key=True)
    otpusk_id = db.Column(db.Integer, nullable=False)
    lang = db.Column(db.Integer, db.ForeignKey('lang.id'), nullable=False)

    name = db.Column(db.String(255), nullable=False)
    country = db.Column(db.Integer, nullable=False)
    iata = db.Column(db.CHAR(3), nullable=False)
