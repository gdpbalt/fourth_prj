import datetime
import json
import math
from typing import Optional

from sqlalchemy import exc

from control import app, db, TourSearch, TourError, Tour
from control.classes.api_otpusk_search_get import MethodSearchGet
from control.settings import LANGS, STATIC_DATA, OUR_SITE
from control.utils.convert import parse_float, parse_date, decimal2str_with_space
from control.utils.dictionary import get_country_name, get_city_name, get_from_city_name, get_operators
from control.utils.lang import location_from, date_duration


class MethodSearch:
    def __init__(self, url_link, index: int):
        self.link: str = url_link
        self.index: int = index
        self.tour: Optional[Tour] = None
        self.log_prefix: Optional[str] = None
        self.error_name: str = 'Ошибка данных'
        self.obj_search: Optional[MethodSearchGet] = None
        self.hotel_min_offer: Optional[dict] = None

    def get_data_from_db(self):
        self.tour = Tour.query.get(self.index)
        if self.tour is None:
            msg = f'Tour id={self.index} not found in database'
            app.logger.error(msg)
            raise ValueError(msg)
        self.log_prefix = 'Tour {}/{}'.format(self.tour.showcase_id, self.tour.id)

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

    def get_best_hotel(self, hotels_record: dict, dept_record: dict):
        hotels_first_record = dict()
        for key, value in hotels_record.items():
            hotels_first_record = value
            break

        hotels_list = list()
        for hotel_id, hotel_detail in hotels_first_record.items():
            offers = hotel_detail.pop('offers', dict())
            hotel_detail['offer'] = self.get_best_offer(offers)
            hotel_detail['hotelId'] = hotel_id
            hotels_list.append(hotel_detail)

        if len(hotels_list) > 0:
            hotels_list.sort(key=lambda el: el['offer']['p'])
            hotels_list[0]['dept'] = dept_record
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
        msg = '{}. {}. {}'.format(error_text, self.log_prefix, error_description[:200])
        app.logger.warning(msg)

        self.tour.errors += 1

        error = TourError()
        error.showcase_id = self.tour.showcase_id
        error.tour_id = self.tour.id
        error.name = error_text
        error.description = error_description[:200]
        error.errors = self.tour.errors

        try:
            db.session.add(error)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            msg = f'Error work with database. {e}'
            app.logger.error(msg)
            raise ConnectionError(msg)

    def get_data_from_api(self):
        self.obj_search = MethodSearchGet(url_link=self.link, log_prefix=self.log_prefix)
        return self.obj_search.run()

    def run(self) -> bool:
        self.get_data_from_db()

        if self.get_data_from_api() is False:
            self.save_error(error_text=self.obj_search.error_name,
                            error_description=self.obj_search.error_full)
            return False

        dept_record = self.obj_search.result.get('dept')
        if not isinstance(dept_record, dict):
            self.save_error(error_text=self.error_name,
                            error_description='Error get data from response. Dict dept is empty. JSON={}'.format(
                                self.obj_search.result))
            return False

        hotels_record = self.obj_search.result.get('hotels')
        if not isinstance(hotels_record, dict):
            self.save_error(error_text=self.error_name,
                            error_description='Error get data from response. Dict hotels is empty. JSON={}'.format(
                                self.obj_search.result))
            return False

        self.hotel_min_offer = self.get_best_hotel(hotels_record=hotels_record, dept_record=dept_record)
        if bool(self.hotel_min_offer) is False:
            self.save_error(error_text=self.error_name,
                            error_description='Error get data from response. Result is empty. JSON={}'.format(
                                self.obj_search.result))
            return False

        self.update_database(hotel_min_offer=self.hotel_min_offer)

        return True
