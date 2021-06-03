from flask import render_template, redirect, make_response, url_for
from flask_security import roles_accepted, current_user, url_for_security, auth_required

from control import app


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for_security('login'))

    else:
        if current_user.has_role('staff'):
            return redirect(url_for('welcome'))
        if current_user.has_role('superuser'):
            return redirect(url_for('superuser'))
        else:
            return redirect(url_for('welcome'))


@app.route('/welcome')
@auth_required()
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


@app.route("/status")
@auth_required()
def status_check():
    app.logger.debug(f"debug log")
    app.logger.info("info log")
    app.logger.warning("warning log")
    app.logger.error("error log")

    return make_response("OK", 200)
