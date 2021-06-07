from flask import render_template, redirect, url_for
from flask_security import roles_accepted, current_user, url_for_security, auth_required, login_user

from config import basedir
from control import app, user_datastore, db, config_name


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for_security('login'))

    else:
        if current_user.has_role('superuser'):
            return redirect(url_for('superuser'))

        if current_user.has_role('staff'):
            return redirect(url_for('welcome'))

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
    app.logger.debug(f"app.config.__class__.__name__={app.config.__class__.__name__}")
    app.logger.debug(f"config_name={config_name}")
    app.logger.debug(f"basedir={basedir}")

    app.logger.debug(f"LOG_LEVEL={app.config['LOG_LEVEL']}")
    app.logger.debug(f"LOG_SCREAM_USE={app.config['LOG_SCREAM_USE']}")
    app.logger.debug(f"LOG_FILE_USE={app.config['LOG_FILE_USE']}, LOG_FILE_NAME={app.config['LOG_FILE_NAME']}")
    app.logger.debug(f"LOG_FILE_ROTATE_USE={app.config['LOG_FILE_ROTATE_USE']}, "
                     f"LOG_FILE_ROTATE_NAME={app.config['LOG_FILE_ROTATE_NAME']}")
    app.logger.debug(f"LOG_SYSLOG_USE={app.config['LOG_SYSLOG_USE']}, LOG_SYSLOG_ADDR={app.config['LOG_SYSLOG_ADDR']}, "
                     f"LOG_SYSLOG_PORT={app.config['LOG_SYSLOG_PORT']}")

    app.logger.debug("debug log")
    app.logger.info("info log")
    app.logger.warning("warning log")
    app.logger.error("error log")
    return render_template('status.html')


@app.before_first_request
def login_admin():
    app.logger.info("Run: before_first_request")
    user = user_datastore.find_user(email=app.config['DEFAULT_ADMIN_EMAIL'], case_insensitive=True)
    if user is None:
        role = user_datastore.find_role(app.config['DEFAULT_ADMIN_ROLE'])
        admin = user_datastore.create_user(email=app.config['DEFAULT_ADMIN_EMAIL'],
                                           password=app.config['DEFAULT_ADMIN_PASSWORD'],
                                           roles=[role])
        db.session.commit()
        login_user(admin)
