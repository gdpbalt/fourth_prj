import datetime
import json
import math
from time import sleep

from sqlalchemy import exc

from control import app, db, TourSearch, TourError, Tour
from control.settings import LANGS, STATIC_DATA, OUR_SITE, SEARCH_SLEEP_WAIT_LASTRESULT_SECOND
from control.utils.convert import parse_float, parse_date, decimal2str_with_space
from control.utils.dictionary import get_country_name, get_city_name, get_from_city_name, get_operators
from control.utils.lang import location_from, date_duration
from control.utils.request import get_data_from_request


class MethodSearch:
    REQUESTS_MAX = 10

    def __init__(self, url_link, index: int):
        self.link = url_link
        self.index = index
        self.tour = None
        self.msg = None

    def get_data_from_db(self):
        self.tour = Tour.query.get(self.index)
        if self.tour is None:
            msg = f'Tour id={self.index} not found in database'
            app.logger.error(msg)
            raise ValueError(msg)
        self.msg = 'Showcase={}, Tour={}'.format(self.tour.showcase_id, self.tour.id)

    @staticmethod
    def get_best_offer(hotel_offers):
        offers_list = list()
        for offer_el in hotel_offers.values():
            offers_list.append(offer_el)

        if len(offers_list) > 0:
            offers_list.sort(key=lambda el: el['p'])
            return offers_list[0]
        else:
            return dict()

    def get_best_hotel(self, data_from_method):
        city_from = data_from_method.get('dept')
        if not isinstance(city_from, dict):
            return dict()

        hotels_list_get = data_from_method.get('hotels')
        if not isinstance(hotels_list_get, dict):
            return dict()

        hotels = hotels_list_get.get('1', dict())
        if hotels is None or not isinstance(hotels, dict):
            return dict()

        hotels_list = list()
        for hotel_id, hotel_detail in hotels.items():
            offers = hotel_detail.pop('offers', dict())
            hotel_detail['offer'] = self.get_best_offer(offers)
            hotel_detail['hotelId'] = hotel_id
            hotels_list.append(hotel_detail)

        if len(hotels_list) > 0:
            hotels_list.sort(key=lambda el: el['offer']['p'])
            hotels_list[0]['dept'] = city_from
            return hotels_list[0]
        else:
            return dict()

    @staticmethod
    def set_database_table(table: TourSearch, hotel_min_offer: dict, lang):
        lang_id = LANGS.index(lang)

        offer_p_value = parse_float(hotel_min_offer['offer']['p'])
        offer_pl_value = parse_float(hotel_min_offer['offer']['pl'])
        tour_date_start = parse_date(hotel_min_offer['offer']['d'])
        promo = hotel_min_offer['offer']['s'].lower() if 's' in hotel_min_offer['offer'] else ''

        table.src_json = json.dumps(hotel_min_offer)
        table.tour_api_id = hotel_min_offer['offer']['i']

        table.hotelId = hotel_min_offer['hotelId']
        table.imgSrc = 'https://newimg.otpusk.com/2/400x300/' + hotel_min_offer['f']
        table.hotelName = hotel_min_offer['n']
        table.hotelStars = hotel_min_offer['s'] + '*'
        table.fullHotelName = table.hotelName + ' ' + table.hotelStars

        table.countryId = hotel_min_offer['t']['i']
        table.countryName = get_country_name(country_id=table.countryId, lang_id=lang_id)

        table.cityId = hotel_min_offer['c']['i']
        table.cityName = get_city_name(city_id=table.cityId, lang_id=lang_id)
        table.resortName = table.cityName

        table.cityFromId = hotel_min_offer['dept']['id']
        table.cityFrom = get_from_city_name(city_from_id=table.cityFromId, lang_id=lang_id)

        table.transport = hotel_min_offer['offer']['t']
        table.locationFromString = location_from(STATIC_DATA[lang]['transport'][table.transport], table.cityFrom,
                                                 lang=lang)

        table.food = hotel_min_offer['offer']['f']
        table.foodString = STATIC_DATA[lang]['food'][table.food].title()

        table.operatorId = hotel_min_offer['offer']['oi']
        table.operatorName = get_operators(operator_id=table.operatorId, lang_id=lang_id)

        table.length = hotel_min_offer['offer']['l']
        table.dateString = hotel_min_offer['offer']['d']
        table.dateDurationString = date_duration(tour_date_start, table.length, lang=lang)

        table.promo = True if promo == 'promo' else False
        table.currency = hotel_min_offer['offer']['u'].lower()
        table.price = decimal2str_with_space(math.ceil(offer_p_value))
        table.priceUah = decimal2str_with_space(math.ceil(offer_pl_value))
        table.priceUahOne = decimal2str_with_space(math.ceil(offer_pl_value / 2))
        table.priceUsd = table.price if table.currency == 'usd' else None
        table.priceEuro = table.price if table.currency == 'eur' else None

        table.update = datetime.datetime.now()
        return table

    @staticmethod
    def make_link_for_table(hotel_min_offer: dict):
        link = OUR_SITE
        link += '/' + hotel_min_offer['t']['c']
        link += '/' + hotel_min_offer['h']
        link += '/' + hotel_min_offer['hotelId']
        link += '/' + str(hotel_min_offer['offer']['i'])
        return link

    def update_database(self, hotel_min_offer):
        for lang_id, lang_name in enumerate(LANGS):
            tour = TourSearch.query.filter_by(tour_id=self.index, lang=lang_id).first()
            if tour is None:
                is_update = False

                tour = TourSearch()
                tour.tour_id = self.index
                tour.lang = lang_id
            else:
                is_update = True

            tour.tourLink = self.make_link_for_table(hotel_min_offer=hotel_min_offer)
            tour = self.set_database_table(table=tour, hotel_min_offer=hotel_min_offer, lang=lang_name)

            self.tour.errors = 0
            try:
                if not is_update:
                    db.session.add(tour)
                db.session.commit()
            except exc.SQLAlchemyError as e:
                msg = f'Error work with database. {e}'
                app.logger.error(msg)
                raise ConnectionError(msg)

    def save_error(self, error_text, error_description):
        msg = '{}. {}. {}'.format(error_text, self.msg, error_description)
        app.logger.warning(msg)

        self.tour.errors += 1

        error = TourError()
        error.showcase_id = self.tour.showcase_id
        error.tour_id = self.tour.id
        error.name = error_text
        error.description = error_description
        error.errors = self.tour.errors

        try:
            db.session.add(error)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            msg = f'Error work with database. {e}'
            app.logger.error(msg)
            raise ConnectionError(msg)

    def run(self):
        self.get_data_from_db()

        is_ok, result = False, None
        for attempt in range(self.REQUESTS_MAX):
            if attempt > 0:
                app.logger.info(f'Sleep {SEARCH_SLEEP_WAIT_LASTRESULT_SECOND} seconds between send requests')
                sleep(SEARCH_SLEEP_WAIT_LASTRESULT_SECOND)

            app.logger.info(f'{self.msg}. Try to get data (retry:{attempt + 1})')
            result = get_data_from_request('{}&number={}'.format(self.link, attempt + 1))
            if result is None:
                self.save_error(error_text='Ошибка получения результа от сервера',
                                error_description=f'Error response from server. URL={self.link}')
                return

            response = result.get('lastResult')
            if response is not None and result['lastResult']:
                app.logger.info(f'{self.msg}. Return lastResult: True')
                is_ok = True
                break
            else:
                app.logger.info(f'{self.msg}. Return lastResult: False or not found')

        if is_ok is False:
            self.save_error(error_text='Ошибка получения результа от сервера',
                            error_description=f'Error response from server. URL={self.link}' +
                                              f' (lastResult=False or not found).' +
                                              f'JSON={result}')
            return

        hotel_min_offer = self.get_best_hotel(data_from_method=result)
        if bool(hotel_min_offer):
            self.update_database(hotel_min_offer=hotel_min_offer)
        else:
            self.save_error(error_text='Ошибка данных',
                            error_description=f'Error get data from response. URL={self.link}.' +
                                              f' (result is empty).' +
                                              f'JSON={result}')
            return

        return True
