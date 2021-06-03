from flask import render_template
from flask_security import roles_accepted

from control import app


@app.route("/superuser/")
@roles_accepted('superuser')
def superuser():
    return render_template('superuser/index.html')
