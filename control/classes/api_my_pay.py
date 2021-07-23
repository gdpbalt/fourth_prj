from typing import Optional

from flask import make_response, jsonify, Request, Response
from pydantic import ValidationError

from control import app
from control.models.api_pay_before_data import PayBeforeData
from control.settings.myapi import MYAPI_HEADERS


class PayBefore:
    ERROR_DEFAULT = 'Some error occurred'
    ERROR_DATA_EMPTY = 'Input data is empty'
    ERROR_VALIDATE = 'Validation error'

    def __init__(self, input_request: Request):
        self.request = input_request
        self.error_text: Optional[str] = None
        self.data: Optional[PayBeforeData] = None

    def parse_data(self) -> bool:
        try:
            content = self.request.get_json()
        except Exception as error_msg:
            self.error_text = '{}. {}'.format(self.ERROR_DEFAULT, error_msg)
            app.logger.warning(self.error_text)
            return False

        if content is None:
            self.error_text = self.ERROR_DATA_EMPTY
            app.logger.warning(self.error_text)
            return False

        try:
            self.data = PayBeforeData(**content)
        except ValidationError as error_msg:
            self.error_text = '{}. {}'.format(self.ERROR_VALIDATE, error_msg)
            app.logger.warning(self.error_text)
            return False

        return True

    def save_data(self) -> bool:
        self.error_text = ''
        return True

    def run(self) -> Response:
        if self.parse_data() is False:
            return make_response(jsonify({'error': self.error_text}), 404, MYAPI_HEADERS)

        if self.save_data() is False:
            return make_response(jsonify({'error': self.error_text}), 404, MYAPI_HEADERS)

        return make_response(self.data.json(by_alias=True), MYAPI_HEADERS)
