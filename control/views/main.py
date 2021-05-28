from flask_security import login_required, roles_accepted, current_user
from flask import render_template, redirect, url_for

from control import app


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('not_auth/index.html')
    return redirect(url_for('protected'))


@app.route('/protected')
@login_required
def protected():
    if current_user.has_role('staff'):
        return render_template('role_guest/index.html')

    elif current_user.has_role('admin'):
        return render_template('role_guest/index.html')

    else:
        return render_template('role_guest/index.html')


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
