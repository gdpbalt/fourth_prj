from control.models import Showcase

HOT_BLOCK = {
    "block": {
        "block_id": "",
        "caption": "",
        "short_desc": "",
        "price_type": "1",
        "client_id": "1",
        "location_url": "",
        "view_type": "tiles",
        "lang": "ua",
        "click_action": "tour",
        "updateTime": ""
    },
    "tours": list(),
    "css": "",
    "api_version": "1",
    "time": 0
}


class HotBlock:
    def __init__(self, index, lang_id):
        self.index = index
        self.lang_id = lang_id
        self.data = None
        self.response = None

    def get_data_from_db(self):
        self.data: Showcase = Showcase.query.get(self.index)

    def make_response(self):
        self.response = HOT_BLOCK
        self.response['block']['block_id'] = str(self.index)
        self.response['block']['caption'] = self.data.name
        self.response['block']['lang'] = 'ua' if self.lang_id == 1 else 'ru'

        self.response['tours'] = list()
        for record in self.data.tours:
            if record.active is True:
                self.response['tours'].append(str(record.id))

    def run(self):
        self.get_data_from_db()
        self.make_response()
