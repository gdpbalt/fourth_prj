from flask import render_template, request

from control import app


@app.errorhandler(404)
def page_not_found(e):
    app.logger.info("404: page not found (url={}, {})".format(request.base_url, e))
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error("500: internal server error (url={}, form={}, {})".format(
        request.base_url, request.form, e))
    return render_template('500.html'), 500
