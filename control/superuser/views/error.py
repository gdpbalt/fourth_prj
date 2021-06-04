from flask import render_template
from flask_security import roles_accepted

from control import app
from control.models import TourError

ERROR_LINE_LIMIT = 25


@app.route("/superuser/error")
@roles_accepted('superuser')
def error():
    errors = TourError.query.order_by(TourError.update.desc()).limit(ERROR_LINE_LIMIT).all()
    return render_template("superuser/errors.html", errors=errors)
