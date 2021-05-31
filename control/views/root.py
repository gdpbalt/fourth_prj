from flask import render_template, redirect, make_response
from flask_security import login_required, roles_accepted, current_user, url_for_security

from control import app


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for_security('login'))

    else:
        if current_user.has_role('staff'):
            return render_template('welcome.html')
        if current_user.has_role('admin'):
            return render_template('welcome.html')
        else:
            return render_template('welcome.html')


@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')


@app.route('/guest')
@roles_accepted('guest')
def role_guest():
    return '<h1>There is for guest only</h1>'


@app.route('/staff')
@roles_accepted('staff')
def role_staff():
    return '<h1>There is for staff only</h1>'


@app.route('/admin')
@roles_accepted('admin')
def role_admin():
    return '<h1>There is for admin only</h1>'


@app.route("/status")
@login_required
def health_check():
    app.logger.debug(f"debug log")
    app.logger.info("info log")
    app.logger.warning("warning log")
    app.logger.error("error log")

    return make_response("OK", 200)
