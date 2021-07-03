import json
import math
from typing import Optional

from pydantic import ValidationError
from sqlalchemy import exc

from control import LANGS, TourSearch, db, app, Tour
from control.models.api_optusk_search_data import ModelTourData
from control.settings import OUR_SITE, STATIC_DATA
from control.utils.convert import decimal2str_with_space
from control.utils.dictionary import get_country_name, get_city_name, get_from_city_name, get_operators, get_iata_city
from control.utils.lang import location_from, date_duration


class MethodSearchSave:
    ERR_VALIDATION = 'Error validation input data'
    ERR_DATABASE = 'Error work with database'

    def __init__(self, input_data: dict, index: int):
        self.input_data: dict = input_data
        self.index: int = index
        self.data: Optional[ModelTourData] = None
        self.error_name: Optional[str] = None
        self.error_full: Optional[str] = None

    def set_error(self, name, text=''):
        self.error_name, self.error_full = (name, text)

    def fill_fields(self, lang_id: int, lang_name: str):
        self.data.op_full_hotel_name = "{} {}".format(self.data.hotel_name, self.data.hotel_stars)

        self.data.op_country_name = get_country_name(country_id=self.data.country_to.id, lang_id=lang_id)
        self.data.op_city_to_name = get_city_name(city_id=self.data.city_to.id, lang_id=lang_id)
        self.data.op_city_from_name = get_from_city_name(city_from_id=self.data.city_from.id, lang_id=lang_id)
        self.data.op_operator_name = get_operators(operator_id=self.data.offer.operator_id, lang_id=lang_id)

        self.data.op_location_from_string = location_from(
            STATIC_DATA[lang_name]['transport'][self.data.offer.transport_type],
            self.data.op_city_from_name,
            lang=lang_name)
        self.data.op_food_string = STATIC_DATA[lang_name]['food'][self.data.offer.food].title()
        self.data.op_date_duration_string = date_duration(self.data.offer.tour_start,
                                                          self.data.offer.length, lang=lang_name)

        self.data.op_promo = True if self.data.offer.promo == 'promo' else False
        self.data.op_price = decimal2str_with_space(math.ceil(self.data.offer.sum_currency))
        self.data.op_price_uah = decimal2str_with_space(math.ceil(self.data.offer.sum_uah))
        self.data.op_price_uah_one = decimal2str_with_space(math.ceil(self.data.offer.sum_uah / 2))
        self.data.op_price_usd = self.data.offer.sum_currency if self.data.offer.currency == 'usd' else None
        self.data.op_price_euro = self.data.offer.sum_currency if self.data.offer.currency == 'usd' == 'eur' else None

        self.data.op_src_json = json.dumps(self.input_data)

        self.data.op_link = self.make_link_for_table()

        if len(self.data.offer.transport.transport_from) > 0:
            transport = self.data.offer.transport.transport_from[0]
            if len(transport.port_from) >= 3:
                city = get_iata_city(iata_code=transport.port_from[:3], lang_id=lang_id)
                if city is not None:
                    self.data.op_port_from_name = city

            if len(transport.port_to) >= 3:
                city = get_iata_city(iata_code=transport.port_to[:3], lang_id=lang_id)
                if city is not None:
                    self.data.op_port_to_name = city

    def make_link_for_table(self):
        data_list = (OUR_SITE,
                     self.data.country_to.country,
                     self.data.hotel_name_snake,
                     self.data.hotel_id,
                     str(self.data.offer.tour_api_id))
        return '/'.join(data_list)

    def set_database_table(self, table: TourSearch):
        table.src_json = json.dumps(self.input_data)
        table.tour_api_id = self.data.offer.tour_api_id

        table.hotelId = self.data.hotel_id
        table.imgSrc = self.data.image
        table.hotelName = self.data.hotel_name
        table.hotelStars = self.data.hotel_stars
        table.fullHotelName = self.data.op_full_hotel_name

        table.countryId = self.data.country_to.id
        table.countryName = self.data.op_country_name

        table.cityId = self.data.city_to.id
        table.cityName = self.data.op_city_to_name
        table.resortName = self.data.op_city_to_name

        table.cityFromId = self.data.city_from.id
        table.cityFrom = self.data.op_city_from_name

        table.transport = self.data.offer.transport_type
        table.locationFromString = self.data.op_location_from_string

        table.food = self.data.offer.food
        table.foodString = self.data.op_food_string

        table.operatorId = self.data.offer.operator_id
        table.operatorName = self.data.op_operator_name

        table.length = self.data.offer.length
        table.dateString = self.data.offer.tour_start
        table.dateDurationString = self.data.op_date_duration_string

        table.promo = self.data.op_promo
        table.currency = self.data.offer.currency
        table.price = self.data.op_price
        table.priceUah = self.data.op_price_uah
        table.priceUahOne = self.data.op_price_uah_one
        table.priceUsd = self.data.op_price_usd
        table.priceEuro = self.data.op_price_euro

        table.update = self.data.op_update

        table.tourLink = self.make_link_for_table()
        return table

    def update_table_tour_search(self, lang_id: int, lang_name: str) -> bool:
        tour_search = TourSearch.query.filter_by(tour_id=self.index, lang=lang_id).first()
        is_update = True
        if tour_search is None:
            is_update = False

            tour_search = TourSearch()
            tour_search.tour_id = self.index
            tour_search.lang = lang_id

        tour_search = self.set_database_table(table=tour_search)
        try:
            if is_update is False:
                db.session.add(tour_search)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            msg = f'Error work with database. {e}'
            app.logger.error(msg)
            self.set_error(name=self.ERR_DATABASE, text=str(e))
            return False
        return True

    def update_table_tour(self) -> bool:
        tour = Tour.query.get(self.index)
        tour.errors = 0
        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            msg = f'Error work with database. {e}'
            app.logger.error(msg)
            self.set_error(name=self.ERR_DATABASE, text=str(e))
            return False
        return True

    def run(self) -> bool:
        try:
            self.data = ModelTourData(**self.input_data)
        except ValidationError as error_msg:
            self.set_error(name=self.ERR_VALIDATION, text=str(error_msg))
            return False

        for lang_id, lang_name in enumerate(LANGS):
            self.fill_fields(lang_id=lang_id, lang_name=lang_name)
            result = self.update_table_tour_search(lang_id=lang_id, lang_name=lang_name)
            if result is False:
                return False

        result = self.update_table_tour()
        if result is False:
            return False

        return True
