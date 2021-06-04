# -*- coding: utf-8 -*-
import argparse
import datetime
from time import sleep

from control import db, app
from control.classes.api_otpusk_search import MethodSearch
from control.models import Tour, TourSearch
from control.settings import SEARCH_UPDATE_MINUTES, SEARCH_TRY_AFTER_ERROR_HOURS, LANGS, SEARCH_STOP_AFTER_ERRORS, \
    SEARCH_PAUSE_BETWEEN_REQUEST_SECOND, SEARCH_STOP_AFTER_SECOND


def run_search():
    datetime_format = '%Y-%m-%d %H:%M:%S'
    start_time = datetime.datetime.now()
    date_search = start_time - datetime.timedelta(minutes=SEARCH_UPDATE_MINUTES)
    date_search_after_error = start_time - datetime.timedelta(hours=SEARCH_TRY_AFTER_ERROR_HOURS)

    lang_id = LANGS.index('rus')
    sql = db.session.query(Tour.showcase_id, Tour.id, TourSearch.update, Tour.link)
    sql = sql.outerjoin(TourSearch, Tour.id == TourSearch.tour_id)

    sql = sql.filter(Tour.active == True)
    sql = sql.filter(db.or_(TourSearch.lang == None, TourSearch.lang == lang_id))
    sql = sql.filter(db.or_(Tour.errors < SEARCH_STOP_AFTER_ERRORS, Tour.errors_update <= date_search_after_error))
    sql = sql.filter(db.or_(TourSearch.update == None, TourSearch.update <= date_search))

    sql = sql.order_by(TourSearch.update)
    sql = sql.all()

    app.logger.info('*** Start searching at {}. Total {} records'.format(
        start_time.strftime(datetime_format), len(sql)))
    app.logger.info('*** Search tours where last updated less than {} and last error less than {}'.format(
        date_search.strftime(datetime_format), date_search_after_error))

    number = 0
    for showcase, tour, update, link in sql:
        if number > 0:
            app.logger.info(f'*** Sleep {SEARCH_PAUSE_BETWEEN_REQUEST_SECOND} seconds between requests to Otpusk')
            sleep(SEARCH_PAUSE_BETWEEN_REQUEST_SECOND)

        number += 1
        app.logger.info("*** Record={}, showcase={}, tour={}, last updated={}".
                        format(number, showcase, tour,
                               update.strftime(datetime_format) if update is not None else 'Null'))
        try:
            search_request = MethodSearch(index=tour, url_link=link)
            search_request.run()
        except Exception as e:
            msg = f'Some error occured. {e}'
            app.logger.error(msg)

        stop_time = datetime.datetime.now()
        delay = stop_time - start_time
        if delay.total_seconds() > SEARCH_STOP_AFTER_SECOND:
            break

    stop_time = datetime.datetime.now()
    delay = stop_time - start_time
    app.logger.info('*** Stop searching at {}. Proccessing {} records in {:.2f} minutes ***'.
                    format(stop_time.strftime(datetime_format), number, delay.total_seconds()/60))


if __name__ == "__main__":
    cmd = argparse.ArgumentParser()
    cmd.add_argument('--run', dest='run', action='store_const',
                     const=True,
                     help="Run search request to old result")

    args = cmd.parse_args()
    if args.run:
        run_search()
