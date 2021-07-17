import datetime
import os
from time import sleep
from typing import Optional

from control import app, Tour
from control.settings import SEARCH_SLEEP_WAIT_LASTRESULT_SECOND
from control.utils.request import get_data_from_request


class MethodSearchGet:
    REQUESTS_MAX = 10
    TEXT_LIMIT_LENGTH = 200
    FORBIDDEN_MINUTES = 10

    ERR_RETURN_EMPTY = 'Error response from server. Return None'
    ERR_LASTRESULT_EMPTY = 'Error response from server. Return lastResult: None or False'
    ERR_HOTELS_EMPTY = 'Error response from server. Field hotels is None'

    def __init__(self, url_link: str, index: int, log_prefix: str, mode: str = 'auto'):
        self.link: str = url_link
        self.index: int = index
        self.log_prefix: str = log_prefix
        self.mode: str = mode
        self.error_name: Optional[str] = None
        self.error_full: Optional[str] = None
        self.result: Optional[dict] = None
        self.date_forbidden = datetime.datetime.now() - datetime.timedelta(minutes=self.FORBIDDEN_MINUTES)

    def set_error(self, name, text=''):
        self.error_name, self.error_full = (name, text)

    @staticmethod
    def request(url):
        return get_data_from_request(url)

    @staticmethod
    def pause(count):
        if count > 1:
            app.logger.info('Sleep {} seconds between requests'.format(SEARCH_SLEEP_WAIT_LASTRESULT_SECOND))
            sleep(SEARCH_SLEEP_WAIT_LASTRESULT_SECOND)

    def is_present_parallel_process(self) -> bool:
        if self.mode == 'manual':
            return False

        tour = Tour.query.get(self.index)
        if tour is None:
            msg = f'Tour id={self.index} not found in database'
            app.logger.error(msg)
            raise ValueError(msg)

        if tour.manual_update_date is None or tour.manual_update_pid is None:
            return False

        if tour.manual_update_date >= self.date_forbidden:
            app.logger.info('{}. Found parrallel process {}. Updated {}'.format(
                tour.manual_update_pid, tour.manual_update_date))
            return True

        return False

    def run(self) -> bool:
        for attempt in range(1, self.REQUESTS_MAX + 1):
            self.pause(count=attempt)

            self.is_present_parallel_process()

            app.logger.info('{}. Try to get data (retry: {})'.format(self.log_prefix, attempt))
            self.result = self.request(url=f'{self.link}&number={attempt}')
            if self.result is None:
                self.set_error(self.ERR_RETURN_EMPTY)
                return False

            response = self.result.get('lastResult')
            if response is not None and response is True:
                app.logger.info(f'{self.log_prefix}. Return lastResult: True. Result is found')
                break
            else:
                app.logger.info(f'{self.log_prefix}. Return lastResult: None or False')

        else:
            self.set_error(self.ERR_LASTRESULT_EMPTY, 'JSON={}'.format(self.result))
            return False

        response = self.result.get('hotels')
        if response is None or response is False:
            self.set_error(self.ERR_HOTELS_EMPTY)
            return False

        return True
