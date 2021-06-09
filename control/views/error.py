import traceback

from flask import render_template, request

from control import app


@app.errorhandler(404)
def page_not_found(e):
    app.logger.info("Page not found (url={}, {})".format(request.base_url, e))
    return render_template('404.html'), 404


@app.errorhandler(Exception)
def all_exception_handler(e):
    error = str(traceback.format_exc())
    app.logger.error("Internal server error (url={}, form={}, {}, {})".format(
        request.base_url, request.form, e, error))
    return render_template('500.html'), 500
