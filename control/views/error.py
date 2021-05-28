from flask import render_template

from control import app


@app.errorhandler(404)
def page_not_found(e):
    # app.logger.info(f"404: page not found. {request.base_url}")
    return render_template('error/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    # app.logger.error(f"500: internal server error. {request.base_url}. {request.form}")
    return render_template('error/500.html'), 500
