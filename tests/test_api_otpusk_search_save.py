import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock

from control.classes.api_otpusk_search_save import MethodSearchSave


class TestMethodSearchSave(TestCase):
    input_data_empty = {}
    input_data_ok = {
        'c': {'i': 715, 'c': 'sharm_el_sheyh', 'n': 'Шарм эль Шейх', 'p': 'Шарм эль Шейхе'},
        't': {'i': 43, 'c': 'egypt', 'cid': 'eg', 'n': 'Египет', 'vs': ''},
        'i': 19455,
        's': '4',
        'p': 22498.89,
        'po': 824.93,
        'a': '',
        'e': ['a_la_carte', 'aerobics', 'cafe', 'chairs', 'childpool', 'conversion', 'crib', 'diving', 'doctor',
              'heated_pool', 'laundry', 'next_beach_line', 'non_smoking', 'outdoor_pool', 'own', 'parking', 'pontoon',
              'restaurant', 'safe', 'sandy', 'surfing', 'table_tennis', 'towels', 'umbrella', 'visa', 'water_sports'],
        'h': 'Palmyra_Amar_El_Zaman_Aqua_Park',
        'f': '00/04/27/66/4276669.jpg',
        'fc': 41,
        'g': {'a': '28.01190', 'o': '34.43092', 'z': '18'},
        'n': 'Palmyra Amar El Zaman Aqua Park',
        'r': 7.1,
        'v': 121,
        'x': 7.7,
        'pu': 'usd',
        'offer': {'last': '2021-06-24 22:39:34',
                  'i': 4161988820839484,
                  'oi': 2835,
                  'ti': 37455,
                  'o': ['insurance', 'transfer'],
                  's': '',
                  'c': 1397,
                  'd': '2021-07-18',
                  'dt': '2021-07-25',
                  'y': 'dbl',
                  'a': 2,
                  'h': 0,
                  'ha': '',
                  'hr': [],
                  'l': 8,
                  'n': 7,
                  'f': 'ai',
                  'ri': 12519,
                  'r': 'Standard Room',
                  'p': 824.93,
                  'pl': 22498.89,
                  'pto': 824.93,
                  'u': 'usd',
                  'ur': 27.2737,
                  'uo': 27.2737,
                  't': 'air',
                  'to': {'from': [{'code': 'PQ 7765', 'craft': 'B-737-800 NG',
                                   'line': 'SkyUp', 'portFr': 'IEV-D', 'portTo': 'SSH', 'begin': '2021-07-18 01:55:00',
                                   'end': '2021-07-18 04:55:00', 'place': '10', 'seats': 'many'}],
                         'to': [{'code': 'PQ 7766', 'craft': 'B-737-800 NG', 'line': 'SkyUp', 'portFr': 'SSH',
                                 'portTo': 'LWO', 'begin': '2021-07-25 05:55:00', 'end': '2021-07-25 11:00:00',
                                 'place': '10', 'seats': 'many'}]}, 'ss': {'hotel': 1, 'avia': 1, 'aviaBack': 1}},
        'hotelId': '19455',
        'dept': {'id': '1397', 'name': 'Львов', 'nameDt': 'Львову', 'namePr': 'Львове', 'nameRd': 'Львова',
                 'nameTr': 'lvov', 'nameVn': 'Львов', 'latLng': {'lat': '49.84100', 'lng': '24.02400', 'zoom': '13'}}}

    def setUp(self):
        self.obj = MethodSearchSave(input_data=dict(), index=1)

        self.obj.update_table_tour_search = MagicMock()
        self.obj.update_table_tour_search.return_value = True

        self.patcher_logger = patch('control.app.logger')
        self.mock_logger = self.patcher_logger.start()

    def tearDown(self):
        self.patcher_logger.stop()

    def test_class_ok(self):
        self.obj.input_data = self.input_data_ok
        result = self.obj.run()
        self.assertTrue(result)

    def test_data_verify_failed(self):
        self.obj.input_data = self.input_data_empty

        result = self.obj.run()
        error = self.obj.error_name
        self.assertFalse(result)
        self.assertEqual(error, self.obj.ERR_VALIDATION)

    def test_update_table_tour_search_failed(self):
        self.obj.input_data = self.input_data_ok
        self.obj.update_table_tour_search.return_value = False

        warning = 'test update_table_tour_search'
        self.obj.error_full = warning

        result = self.obj.run()
        error = self.obj.error_name
        full = self.obj.error_full
        self.assertFalse(result)
        self.assertEqual(error, self.obj.ERR_DATABASE)
        self.assertEqual(full, warning)


if __name__ == '__main__':
    # coverage run -m unittest discover
    # coverage report -m --omit=*\venv\*
    unittest.main()
