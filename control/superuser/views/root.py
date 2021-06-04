from flask import redirect, url_for
from flask_security import roles_accepted

from control import app


@app.route("/superuser/")
@roles_accepted('superuser')
def superuser():
    return redirect(url_for('show'))
