from flask import render_template
from flask_security import roles_accepted

from control import app, db, TourSearch, Tour, Showcase
from control.settings import LANGS

LINE_LIMIT = 100


@app.route("/superuser/success")
@roles_accepted('superuser')
def success():
    lang_id = LANGS.index('rus')

    sql = db.session.query(TourSearch.updated, Tour, Showcase.name)
    sql = sql.filter(TourSearch.lang == lang_id)
    sql = sql.filter(TourSearch.tour_id == Tour.id)
    sql = sql.filter(Tour.showcase_id == Showcase.id)
    sql = sql.order_by(TourSearch.updated.desc())
    sql = sql.limit(LINE_LIMIT)
    data = sql.all()

    return render_template("superuser/success.html", data=data)
