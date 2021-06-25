from control.classes.api_otpusk import MethodOtpusk
from control.settings import API, LANGS
from control.utils.request import get_method_link_prepend, get_method_link_append


class MethodSuggests(MethodOtpusk):
    METHOD = API['method_suggests']

    def __init__(self, text, lang=LANGS[0]):
        self.text = text
        self.lang_name = lang
        self.lang_id = LANGS.index(lang)
        self.link = self.get_method_url()
        super().__init__(link=self.link, lang_id=self.lang_id)

    def get_method_url(self):
        link = '{}text={}&{}&with=price'.format(
            get_method_link_prepend(self.METHOD), self.text, get_method_link_append(lang=self.lang_name))
        return link

    @staticmethod
    def parse_result(input_data: dict):
        output_list = list()
        if input_data is None:
            return output_list
        response = input_data.get('response', list())
        for record in response.values():
            output = dict()
            output['label'] = record['name']
            output['value'] = record['id']
            output_list.append(output)
        return output_list
