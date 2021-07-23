from flask import request

from control import app
from control.classes.api_my_pay import PayBefore


@app.route("/api/pay_after", methods=['GET', 'POST'])
def pay_after():
    return 'pay_after is OK'


@app.route("/api/pay_before", methods=['GET', 'POST'])
def pay_before():
    obj = PayBefore(input_request=request)
    response = obj.run()
    return response
