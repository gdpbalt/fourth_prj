from control.utils.utils_request import get_data_from_request


class MethodError(Exception):
    pass


class MethodOtpusk:
    def __init__(self, link, lang_id):
        self.link = link
        self.lang_id = lang_id
        self.data = None

    def get_data_from_api(self):
        return get_data_from_request(self.link)

    @staticmethod
    def parse_result(input_data: dict):
        return input_data

    def save_data2dbase(self):
        pass

    def run(self):
        reuslt = self.get_data_from_api()
        self.data = self.parse_result(input_data=reuslt)
        self.save_data2dbase()
