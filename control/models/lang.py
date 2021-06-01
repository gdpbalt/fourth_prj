from control import db


class Lang(db.Model):
    __tablename__ = 'lang'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(3), nullable=False)
