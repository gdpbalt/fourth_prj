from control import db


class TourCategory(db.Model):
    __tablename__ = 'tour_category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    order_index = db.Column(db.Integer, server_default=db.text("1"), nullable=False)
    selected = db.Column(db.Boolean, server_default=db.text("false"), nullable=False)

    value = db.Column(db.String(255), nullable=False)


class TourTransport(db.Model):
    __tablename__ = 'tour_transport'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    order_index = db.Column(db.Integer, server_default=db.text("1"), nullable=False)
    selected = db.Column(db.Boolean, server_default=db.text("false"), nullable=False)

    value = db.Column(db.String(255), nullable=False)


class TourFood(db.Model):
    __tablename__ = 'tour_food'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    order_index = db.Column(db.Integer, server_default=db.text("1"), nullable=False)
    selected = db.Column(db.Boolean, server_default=db.text("false"), nullable=False)

    value = db.Column(db.String(255), nullable=False)


class TourLength(db.Model):
    __tablename__ = 'tour_length'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    order_index = db.Column(db.Integer, server_default=db.text("1"), nullable=False)
    selected = db.Column(db.Boolean, server_default=db.text("false"), nullable=False)

    nights_from = db.Column(db.Integer, nullable=False)
    nights_to = db.Column(db.Integer, nullable=False)


class TourFrom(db.Model):
    __tablename__ = 'tour_from'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    order_index = db.Column(db.Integer, server_default=db.text("1"), nullable=False)
    selected = db.Column(db.Boolean, server_default=db.text("false"), nullable=False)

    value = db.Column(db.Integer, nullable=False)


class Lang(db.Model):
    __tablename__ = 'lang'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(3), nullable=False)
