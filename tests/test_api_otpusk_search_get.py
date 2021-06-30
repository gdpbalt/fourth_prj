import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock

from control.classes.api_otpusk_search_get import MethodSearchGet


class TestMethodSearchGet(TestCase):
    arr = dict()
    arr['last_result_false'] = {
        'lastResult': False
    }
    arr['last_result_true'] = {
        'lastResult': True
    }
    arr['hotels_empty'] = {
        'lastResult': True,
        'hotels': None
    }
    arr['hotels_not_empty'] = {
        'lastResult': True,
        'hotels': dict()
    }

    def setUp(self):
        self.obj = MethodSearchGet(url_link='', log_prefix='')
        self.obj.pause = MagicMock()

        self.patcher_logger = patch('control.app.logger')
        self.mock_logger = self.patcher_logger.start()

    def tearDown(self):
        self.patcher_logger.stop()

    def test_request_return_none(self):
        self.obj.request = MagicMock(return_value=None)

        result = self.obj.run()
        error = self.obj.error_name
        self.assertFalse(result)
        self.assertEqual(error, self.obj.ERR_RETURN_EMPTY)

    def test_request_last_result_false(self):
        self.obj.request = MagicMock(return_value=self.arr['last_result_false'])

        result = self.obj.run()
        error = self.obj.error_name
        self.assertFalse(result)
        self.assertEqual(error, self.obj.ERR_LASTRESULT_EMPTY)

    def test_request_last_result_true(self):
        self.obj.request = MagicMock(return_value=self.arr['last_result_true'])

        result = self.obj.run()
        error = self.obj.error_name
        self.assertFalse(result)
        self.assertEqual(error, self.obj.ERR_HOTELS_EMPTY)

    def test_request_hotels_empty(self):
        self.obj.request = MagicMock(return_value=self.arr['hotels_empty'])

        result = self.obj.run()
        error = self.obj.error_name
        self.assertFalse(result)
        self.assertEqual(error, self.obj.ERR_HOTELS_EMPTY)

    def test_request_hotels_not_empty(self):
        self.obj.request = MagicMock(return_value=self.arr['hotels_not_empty'])

        result = self.obj.run()
        self.assertTrue(result)


if __name__ == '__main__':
    # coverage run -m unittest discover
    # coverage report -m --omit=*\venv\*
    unittest.main()
