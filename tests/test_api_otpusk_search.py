import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch

from control.classes.api_otpusk_search import MethodSearch


class TestMethodSearch(TestCase):
    arr = dict()
    arr['hotels_empty'] = {
        'lastResult': True,
        'dept': dict(),
        'hotels': None
    }
    arr['hotels_not_empty'] = {
        'lastResult': True,
        'dept': dict(),
        'hotels': dict()
    }
    arr['hotels_with_data'] = {
        'lastResult': True,
        'dept': {
            'id': '1544',
            'name': 'Киев'
        },
        'hotels': {
            '1': {
                '111': {
                    'offers': {
                        '11111': {
                            'p': 1
                        },
                        '22222': {
                            'p': 2
                        }
                    }
                },
                '222': {
                    'offers': {
                        '3333': {
                            'p': 3
                        },
                        '44444': {
                            'p': 4
                        }
                    }
                }
            }
        }
    }

    def setUp(self):
        self.obj = MethodSearch(url_link='', index=0)
        self.obj.get_data_from_table_tour = MagicMock()
        self.obj.save_error = MagicMock()
        self.obj.get_data_from_api = MagicMock()
        self.obj.save_tour_search2db = MagicMock()
        self.obj.update_table_tour = MagicMock()

        self.obj.obj_search = MagicMock()
        self.obj.obj_search.error_name = ''
        self.obj.obj_search.error_full = ''
        self.obj.obj_search.result = None

        self.patcher_logger = patch('control.app.logger')
        self.mock_logger = self.patcher_logger.start()

    def tearDown(self):
        self.patcher_logger.stop()

    def test_request_return_error(self):
        self.obj.get_data_from_api.return_value = False
        result = self.obj.run()
        self.assertFalse(result)

    def test_request_return_true(self):
        self.obj.get_data_from_api.return_value = True
        self.obj.obj_search.result = dict()

        result = self.obj.run()
        self.assertFalse(result)

    def test_dict_not_empty(self):
        self.obj.get_data_from_api.return_value = True
        self.obj.obj_search.result = self.arr['hotels_empty']

        result = self.obj.run()
        self.assertFalse(result)

    def test_hotels_not_empty(self):
        self.obj.get_data_from_api.return_value = True
        self.obj.obj_search.result = self.arr['hotels_not_empty']

        result = self.obj.run()
        self.assertFalse(result)
        self.assertIsInstance(self.obj.hotel_min_offer, dict)

    def test_true(self):
        self.obj.get_data_from_api.return_value = True
        self.obj.obj_search.result = self.arr['hotels_with_data']

        result = self.obj.run()
        self.assertTrue(result)


if __name__ == '__main__':
    # coverage run -m unittest discover
    # coverage report -m --omit=*\venv\*
    unittest.main()
