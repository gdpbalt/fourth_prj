# -*- coding: utf-8 -*-
import argparse
import datetime
from time import sleep
from typing import Any

from sqlalchemy import exc

from control import db, app, MakeSearchLink
from control.classes.api_otpusk_search import MethodSearch
from control.models import Tour, TourSearch
from control.settings import SEARCH_UPDATE_MINUTES, SEARCH_TRY_AFTER_ERROR_HOURS, LANGS, SEARCH_STOP_AFTER_ERRORS, \
    SEARCH_PAUSE_BETWEEN_REQUEST_SECOND, SEARCH_STOP_AFTER_SECOND, SEARCH_INTERVAL_DAYS, \
    SEARCH_DISABLE_AFTER_FAILED_UPATE_DAYS, SEARCH_DISABLE_AFTER_ERRORS

datetime_format = '%Y-%m-%d %H:%M:%S'


def get_run_search_sql(force_flag: bool, date_search: datetime.datetime,
                       date_search_after_error: datetime.datetime) -> list:
    lang_id = LANGS.index('rus')

    sql = db.session.query(Tour.showcase_id, Tour.id, TourSearch.updated, Tour.link)
    sql = sql.outerjoin(TourSearch, Tour.id == TourSearch.tour_id)
    sql = sql.filter(Tour.active == True)
    sql = sql.filter(db.or_(TourSearch.lang == None, TourSearch.lang == lang_id))
    if force_flag is False:
        sql = sql.filter(db.or_(Tour.errors < SEARCH_STOP_AFTER_ERRORS, Tour.errors_update <= date_search_after_error))
    if force_flag is False:
        sql = sql.filter(db.or_(TourSearch.updated == None, TourSearch.updated <= date_search))
    sql = sql.order_by(TourSearch.updated)
    return sql.all()


def do_run_search(tour_id: int, url_link: str) -> None:
    try:
        search_request = MethodSearch(index=tour_id, url_link=url_link)
        search_request.run()
    except Exception as e:
        msg = f'Some error occurred. {e}'
        app.logger.error(msg)


def get_delay_of_runnig(start_time: datetime) -> int:
    stop_time = datetime.datetime.now()
    delay = stop_time - start_time
    return int(delay.total_seconds())


def get_run_correct_sql(date_now: datetime.date) -> list[Tour]:
    sql = db.session.query(Tour)
    sql = sql.filter(Tour.active == True)
    sql = sql.filter(Tour.date_start <= date_now)
    return sql.all()


def start_search(force_flag: bool = False):
    """
        Обновить данные по турам, которые обновлялись некоторое время тому назад
        В первую очередь запросить информацию по новым турам, по которым нет данных

    :return: None
    """
    number, date_now = 0, datetime.datetime.now()
    date_search = date_now - datetime.timedelta(minutes=SEARCH_UPDATE_MINUTES)
    date_search_after_error = date_now - datetime.timedelta(hours=SEARCH_TRY_AFTER_ERROR_HOURS)
    sql = get_run_search_sql(force_flag=force_flag, date_search=date_search,
                             date_search_after_error=date_search_after_error)

    app.logger.info('*** Start searching at {}. Total {} records'.format(
        date_now.strftime(datetime_format), len(sql)))
    app.logger.info('*** Search tours where last updated less than {} and last error less than {}'.format(
        date_search.strftime(datetime_format), date_search_after_error))

    for showcase, tour, update, link in sql:
        if (number := number + 1) > 1:
            app.logger.info(f'*** Sleep {SEARCH_PAUSE_BETWEEN_REQUEST_SECOND} seconds between Search')
            sleep(SEARCH_PAUSE_BETWEEN_REQUEST_SECOND)

        app.logger.info("*** Record={}, showcase={}, tour={}, last updated={}".format(
            number, showcase, tour, update.strftime(datetime_format) if update is not None else 'Null'))

        do_run_search(tour_id=tour, url_link=link)
        if force_flag is False and get_delay_of_runnig(start_time=date_now) > SEARCH_STOP_AFTER_SECOND:
            break

    app.logger.info('*** Stop searching. Proccessing {} records in {:.2f} minutes ***'.format(
        number, get_delay_of_runnig(start_time=date_now) / 60))


def start_correct_date_start_stop():
    """
    Выбрать туры, дата вылета в которые меньше чем завтра. Обновить такие туры (date_start и date_stop)

    :return: None
    """
    date_now = datetime.datetime.now().date()
    date_start = date_now + datetime.timedelta(days=1)
    date_stop = date_start + datetime.timedelta(days=SEARCH_INTERVAL_DAYS)
    sql = get_run_correct_sql(date_now=date_now)

    app.logger.debug(f'*** Сегодня: {date_now}, Завтра: {date_start}, Интервал: {SEARCH_INTERVAL_DAYS} дней, '
                     f'Конечная дата: {date_stop}, Найдено: {len(sql)} туров')
    for tour in sql:
        app.logger.debug(f'Витрина={tour.showcase_id}, Тур={tour.id}, Активный={tour.active}')
        app.logger.debug(f'СТАРОЕ ЗНАЧЕНИЕ: start={tour.date_start}, stop={tour.date_stop}')

        tour.date_start = date_start
        tour.date_stop = date_stop

        try:
            data_link = MakeSearchLink(index=tour.id)
            data_link.run()
            tour.link = data_link.link
        except Exception as e:
            msg = f'Some error occurred. {e}'
            app.logger.error(msg)
            break

        try:
            db.session.commit()
            app.logger.info(f"Данные о туре id={tour.id} успешно обновлены")
        except exc.SQLAlchemyError as e:
            msg = f"При изменении тура id={tour.id} произошла ошибка"
            app.logger.error(f"{msg}. {e}")


def get_disable_failed_tours_sql(date_stop: datetime.date) -> list[Any]:
    lang_id = LANGS.index('rus')
    date_stop_dt = datetime.datetime.combine(date=date_stop, time=datetime.time(hour=0, minute=0, second=0))

    sql = db.session.query(Tour, TourSearch.updated)
    sql = sql.outerjoin(TourSearch, Tour.id == TourSearch.tour_id)
    sql = sql.filter(Tour.active == True)
    sql = sql.filter(db.or_(TourSearch.lang == None, TourSearch.lang == lang_id))
    sql = sql.filter(db.or_(TourSearch.updated <= date_stop_dt, Tour.errors > SEARCH_DISABLE_AFTER_ERRORS))
    sql = sql.order_by(TourSearch.updated)
    return sql.all()


def start_disable_failed_tours():
    """
    Выбрать все туры, которые имеют кол-во ошибок больше заданного уровня значения
    или обновлялись последний раз раньше чем заданный день

    Запретить такие туры к обработке (установить Tour.active = False)

    :return: None
    """
    date_now = datetime.datetime.now().date()
    date_stop_trying = date_now - datetime.timedelta(days=SEARCH_DISABLE_AFTER_FAILED_UPATE_DAYS)
    app.logger.debug('*** Сегодня: {}, не обрабатывать туры старше {} ({} дня назад) или больше чем {} ошибок'.format(
        date_now, date_stop_trying, SEARCH_DISABLE_AFTER_FAILED_UPATE_DAYS, SEARCH_DISABLE_AFTER_ERRORS))

    sql = get_disable_failed_tours_sql(date_stop=date_stop_trying)
    for record in sql:
        tour = record.Tour
        error_updated = record.updated
        print("Showcase={}, Tour={}, Tour.errors={}, TourSearch.updated={}".format(
            tour.showcase_id, tour.id, tour.errors, error_updated))

        tour.active = False
        tour.updated = datetime.datetime.now()


if __name__ == "__main__":
    cmd = argparse.ArgumentParser()
    cmd.add_argument('--run', dest='run', action='store_const',
                     const=True,
                     help="Run search request for old tours (can be used with --force)")
    cmd.add_argument('--correct', dest='correct', action='store_const',
                     const=True,
                     help="Correct date_start/date_stop for search tour")
    cmd.add_argument('--error', dest='error', action='store_const',
                     const=True,
                     help="Disable tours if they have errors last a few days ")

    cmd.add_argument('--force', dest='force', action='store_const',
                     const=True,
                     help="Force some operations")
    args = cmd.parse_args()
    if args.force:
        is_force = True
    else:
        is_force = False

    if args.run:
        start_search(force_flag=is_force)
    elif args.correct:
        start_correct_date_start_stop()
    elif args.error:
        start_disable_failed_tours()
