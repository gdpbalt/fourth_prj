from flask import jsonify
from flask import request
from flask_security import roles_accepted

from control import app
from control.classes.otpusk_suggests import MethodSuggests


@app.route("/suggest")
@app.route("/suggest/<string:term>")
@roles_accepted('admin')
def suggest(term=None):
    if term is None:
        input_string = request.args.get('term', '')
    else:
        input_string = term

    data = MethodSuggests(text=input_string)
    data.run()

    output_list = list()
    for record in data.data:
        output_list.append(record['name'])
    return jsonify(output_list)
