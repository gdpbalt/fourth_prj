from flask import request

from control import app
from control.settings import API, LANGS
from control.utils.request import get_data_from_request


class GetHotBlock:
    METHOD = 'api/hotblock'

    def __init__(self, index, lang_id):
        self.index = index
        self.lang_id = lang_id
        self.link = self.get_link()
        self.data = None

    def get_link(self):
        return '{}{}?blockId={}&{}={}&{}={}'.format(
            request.host_url, self.METHOD, self.index,
            API['lang_name'], LANGS[self.lang_id],
            API['token_name'], app.config['TOKEN'])

    @staticmethod
    def parse_result(input_data: dict):
        if not isinstance(input_data, dict):
            return list()
        response = input_data.get('tours', list())
        return response

    def run(self):
        app.logger.warning(self.link)
        reuslt = get_data_from_request(self.link)
        self.data = self.parse_result(input_data=reuslt)


class GetHotTour(GetHotBlock):
    METHOD = 'api/hotTour'

    @staticmethod
    def parse_result(input_data: dict):
        if isinstance(input_data, dict) is False:
            return

        response = input_data.get('searchedTour')
        if isinstance(response, dict) is False:
            return

        response = response.get('data_view')
        if isinstance(response, dict) is False:
            return

        response['updateTime'] = input_data['updateTime']
        response['errors'] = input_data['errors']
        response['errorLast'] = input_data['errorLast']
        response['number'] = 0
        return response
