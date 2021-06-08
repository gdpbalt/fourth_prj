# -*- coding: utf-8 -*-
import argparse
import datetime
from time import sleep

from sqlalchemy import exc

from control import db, app, MakeSearchLink
from control.classes.api_otpusk_search import MethodSearch
from control.models import Tour, TourSearch
from control.settings import SEARCH_UPDATE_MINUTES, SEARCH_TRY_AFTER_ERROR_HOURS, LANGS, SEARCH_STOP_AFTER_ERRORS, \
    SEARCH_PAUSE_BETWEEN_REQUEST_SECOND, SEARCH_STOP_AFTER_SECOND, SEARCH_INTERVAL_DAYS

datetime_format = '%Y-%m-%d %H:%M:%S'


def run_search():
    """
        Выбрать туры, которые трубуется обновить
        В первую очередь запросить информацию по новым турам
    :return: None
    """
    lang_id = LANGS.index('rus')
    start_time = datetime.datetime.now()
    date_search = start_time - datetime.timedelta(minutes=SEARCH_UPDATE_MINUTES)
    date_search_after_error = start_time - datetime.timedelta(hours=SEARCH_TRY_AFTER_ERROR_HOURS)

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


def run_correct():
    """
    Выбрать туры, дата вылета в которые старше чем завтра и обновить дату вылета

    :return: None
    """
    date_now = datetime.datetime.now().date()
    date_start = date_now + datetime.timedelta(days=1)
    date_stop = date_start + datetime.timedelta(days=SEARCH_INTERVAL_DAYS)

    sql = db.session.query(Tour)
    sql = sql.filter(Tour.active == True)
    sql = sql.filter(Tour.date_start <= date_now)
    sql = sql.all()

    app.logger.debug(f'*** Сегодня: {date_now}, Завтра: {date_start}, Интервал: {SEARCH_INTERVAL_DAYS} дней, '
                     f'Конечная дата: {date_stop}, Найдено: {len(sql)} туров')
    for tour in sql:
        app.logger.debug(f'Витрина={tour.showcase_id}, Тур={tour.id}, Активный={tour.active}')
        app.logger.debug(f'СТАРОЕ ЗНАЧЕНИЕ: start={tour.date_start}, stop={tour.date_stop}')

        tour.date_start = date_start
        tour.date_stop = date_stop

        # TODO проанализировать возможную ошибку, как в методе search
        data_link = MakeSearchLink(index=tour.id)
        data_link.run()
        tour.link = data_link.link

        app.logger.debug(f'НОВОЕ ЗНАЧЕНИЕ: start={tour.date_start}, stop={tour.date_stop}')
        try:
            db.session.commit()
            app.logger.info(f"Данные о туре id={tour.id} успешно обновлены")
        except exc.SQLAlchemyError as e:
            msg = f"При изменении тура id={tour.id} произошла ошибка"
            app.logger.error(f"{msg}. {e}")


if __name__ == "__main__":
    cmd = argparse.ArgumentParser()
    cmd.add_argument('--run', dest='run', action='store_const',
                     const=True,
                     help="Run search request to old result")
    cmd.add_argument('--correct', dest='correct', action='store_const',
                     const=True,
                     help="Correct start/stop of search tour")

    args = cmd.parse_args()
    if args.run:
        run_search()
    if args.correct:
        run_correct()
