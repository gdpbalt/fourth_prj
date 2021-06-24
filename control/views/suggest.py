from flask import jsonify
from flask import request
from flask_security import auth_required

from control import app
from control.classes.otpusk_suggests import MethodSuggests


@app.route("/suggest")
@app.route("/suggest/<string:term>")
@auth_required()
def suggest(term=None):
    if term is None:
        input_string = request.args.get('term', '')
    else:
        input_string = term

    data = MethodSuggests(text=input_string)
    data.run()
    return jsonify(data.data)
