from flask import render_template
from flask_login import login_required

from control import app
from control.models import TourError

ERROR_LINE_LIMIT = 25


@app.route("/admin/error")
@login_required
def error():
    errors = TourError.query.order_by(TourError.update.desc()).limit(ERROR_LINE_LIMIT).all()
    return render_template("admin/errors.html", errors=errors)
