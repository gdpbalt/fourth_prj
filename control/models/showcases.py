from control import db


class Showcase(db.Model):
    __tablename__ = 'showcase'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    order_index = db.Column(db.Integer, server_default=db.text("1"), nullable=False)
    tours = db.relationship('Tour', backref='tour', lazy='joined', order_by=order_index)


class Tour(db.Model):
    __tablename__ = 'tour'

    id = db.Column(db.Integer, primary_key=True)
    showcase_id = db.Column(db.Integer, db.ForeignKey('showcase.id'))
    order_index = db.Column(db.Integer, server_default=db.text("1"), nullable=False)
    active = db.Column(db.Boolean, server_default=db.text("false"), nullable=False)

    destination = db.Column(db.String(255))

    date_start = db.Column(db.Date)
    date_stop = db.Column(db.Date)

    from_id = db.Column(db.Integer, db.ForeignKey('tour_from.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('tour_category.id'))
    transport_id = db.Column(db.Integer, db.ForeignKey('tour_transport.id'))
    food_id = db.Column(db.Integer, db.ForeignKey('tour_food.id'))
    length_id = db.Column(db.Integer, db.ForeignKey('tour_length.id'))

    category = db.relationship('TourCategory', backref='tour_category', lazy='select')
    from_city = db.relationship('TourFrom', backref='tour_from', lazy='select')
    transport = db.relationship('TourTransport', backref='tour_transport', lazy='select')
    food = db.relationship('TourFood', backref='tour_food', lazy='select')
    length = db.relationship('TourLength', backref='tour_length', lazy='select')

    link = db.Column(db.String(255))

    errors = db.Column(db.Integer, nullable=False, server_default=db.text("0"))
    errors_update = db.Column(db.DateTime, nullable=False,
                              server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class TourSearch(db.Model):
    __tablename__ = 'tour_search'
    __table_args__ = (db.UniqueConstraint('tour_id', 'lang', name='_tour_id_lang_uc'),)

    id = db.Column(db.Integer, primary_key=True)
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'), nullable=False)
    lang = db.Column(db.Integer, db.ForeignKey('lang.id'), nullable=False)
    src_json = db.Column(db.Text, nullable=False)
    tour_api_id = db.Column(db.String(255), nullable=False)
    update = db.Column(db.DateTime, nullable=False,
                       server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    hotelId = db.Column(db.Integer, nullable=False)
    imgSrc = db.Column(db.String(255), nullable=False)
    hotelName = db.Column(db.String(255), nullable=False)
    fullHotelName = db.Column(db.String(255), nullable=False)
    hotelStars = db.Column(db.String(255), nullable=False)
    countryId = db.Column(db.Integer, nullable=False)
    countryName = db.Column(db.String(255), nullable=False)
    cityId = db.Column(db.Integer, nullable=False)
    cityName = db.Column(db.String(255), nullable=False)
    resortName = db.Column(db.String(255), nullable=False)
    dateString = db.Column(db.Date, nullable=False)
    cityFromId = db.Column(db.Integer, nullable=False)
    cityFrom = db.Column(db.String(255), nullable=False)
    locationFromString = db.Column(db.String(255), nullable=False)
    foodString = db.Column(db.String(255), nullable=False)
    dateDurationString = db.Column(db.String(255), nullable=False)
    operatorId = db.Column(db.Integer, nullable=False)
    operatorName = db.Column(db.String(255), nullable=False)
    promo = db.Column(db.Boolean, nullable=False)
    price = db.Column(db.String(255), nullable=False)
    currency = db.Column(db.String(255), nullable=False)

    priceUsd = db.Column(db.String(255), nullable=True)
    priceEuro = db.Column(db.String(255), nullable=True)

    priceUah = db.Column(db.String(255), nullable=False)
    priceUahOne = db.Column(db.String(255), nullable=False)
    tourLink = db.Column(db.String(255), nullable=False)
    transport = db.Column(db.String(255), nullable=False)
    food = db.Column(db.String(255), nullable=False)
    length = db.Column(db.Integer, nullable=False)


class TourError(db.Model):
    __tablename__ = 'tour_error'

    id = db.Column(db.Integer, primary_key=True)
    showcase_id = db.Column(db.Integer, db.ForeignKey('showcase.id'), nullable=False)
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'), nullable=False)

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False, default=db.text(''))
    update = db.Column(db.DateTime, nullable=False,
                       server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    errors = db.Column(db.Integer, default=db.text(''))

    showcase = db.relationship('Showcase', backref='showcase', lazy=True, uselist=False)
