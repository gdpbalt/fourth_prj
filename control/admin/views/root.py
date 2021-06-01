from flask import render_template
from flask_security import roles_accepted

from control import app


@app.route("/admin/")
@roles_accepted('admin')
def root():
    return render_template('admin/index.html')


# @app.route("/")
# @roles_accepted('admin')
# def root():
#     return redirect(url_for("show"))
