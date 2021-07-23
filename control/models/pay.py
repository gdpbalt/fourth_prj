from control import db


class Pay(db.Model):
    __tablename__ = 'pay'

    id = db.Column(db.Integer, primary_key=True)
    json_data = db.Column(db.Text, nullable=False)
