import json
import math
from datetime import date, datetime
from pprint import pprint
from typing import Optional

from pydantic import BaseModel, Field, ValidationError, validator

from control import LANGS
from control.settings import STATIC_DATA
from control.utils.convert import decimal2str_with_space
from control.utils.dictionary import get_country_name, get_city_name, get_from_city_name, get_operators, get_iata_city
from control.utils.lang import location_from, date_duration

hotel_min_offer = {
    'c': {'i': 715, 'c': 'sharm_el_sheyh', 'n': 'Шарм эль Шейх', 'p': 'Шарм эль Шейхе'},
    't': {'i': 43, 'c': 'egypt', 'cid': 'eg', 'n': 'Египет', 'vs': ''}, 'i': 19455, 's': '4', 'p': 22498.89,
    'po': 824.93, 'a': '',
    'e': ['a_la_carte', 'aerobics', 'cafe', 'chairs', 'childpool', 'conversion', 'crib', 'diving', 'doctor',
          'heated_pool', 'laundry', 'next_beach_line', 'non_smoking', 'outdoor_pool', 'own', 'parking', 'pontoon',
          'restaurant', 'safe', 'sandy', 'surfing', 'table_tennis', 'towels', 'umbrella', 'visa', 'water_sports'],
    'h': 'Palmyra_Amar_El_Zaman_Aqua_Park', 'f': '00/04/27/66/4276669.jpg', 'fc': 41,
    'g': {'a': '28.01190', 'o': '34.43092', 'z': '18'}, 'n': 'Palmyra Amar El Zaman Aqua Park',
    'r': 7.1, 'v': 121, 'x': 7.7, 'pu': 'usd',
    'offer': {'last': '2021-06-24 22:39:34', 'i': 4161988820839484,
              'oi': 2835, 'ti': 37455, 'o': ['insurance', 'transfer'], 's': '', 'c': 1397, 'd': '2021-07-18',
              'dt': '2021-07-25', 'y': 'dbl', 'a': 2, 'h': 0, 'ha': '', 'hr': [], 'l': 8, 'n': 7, 'f': 'ai',
              'ri': 12519, 'r': 'Standard Room', 'p': 824.93, 'pl': 22498.89, 'pto': 824.93, 'u': 'usd',
              'ur': 27.2737, 'uo': 27.2737, 't': 'air',
              'to': {'from': [{'code': 'PQ 7765', 'craft': 'B-737-800 NG',
                               'line': 'SkyUp', 'portFr': 'IEV-D', 'portTo': 'SSH', 'begin': '2021-07-18 01:55:00',
                               'end': '2021-07-18 04:55:00', 'place': '10', 'seats': 'many'}],
                     'to': [{'code': 'PQ 7766', 'craft': 'B-737-800 NG', 'line': 'SkyUp', 'portFr': 'SSH',
                             'portTo': 'LWO', 'begin': '2021-07-25 05:55:00', 'end': '2021-07-25 11:00:00',
                             'place': '10', 'seats': 'many'}]}, 'ss': {'hotel': 1, 'avia': 1, 'aviaBack': 1}},
    'hotelId': '19455', 'dept': {'id': '1397', 'name': 'Львов', 'nameDt': 'Львову', 'namePr': 'Львове',
                                 'nameRd': 'Львова', 'nameTr': 'lvov', 'nameVn': 'Львов',
                                 'latLng': {'lat': '49.84100', 'lng': '24.02400', 'zoom': '13'}}}


class ModelTransferData(BaseModel):
    begin: datetime
    end: datetime
    port_from: str = Field(alias='portFr')
    port_to: str = Field(alias='portTo')


class ModelTransferFromTo(BaseModel):
    transport_from: list[ModelTransferData] = Field(alias='from')
    transport_to: list[ModelTransferData] = Field(alias='to')


class ModelOffer(BaseModel):
    tour_api_id: int = Field(alias='i')
    tour_start: date = Field(alias='d')

    transport: ModelTransferFromTo = Field(alias='to')
    transport_type: str = Field(alias='t')

    currency: str = Field(alias='u')
    sum_currency: float = Field(alias='p')
    sum_uah: float = Field(alias='pl')
    promo: Optional[str] = Field(alias='s', default='')

    food: str = Field(alias='f')
    operator_id: int = Field(alias='oi')
    length: int = Field(alias='l')

    # noinspection PyMethodParameters
    @validator('promo')
    def transform_promo(cls, v):
        return v.lower()

    # noinspection PyMethodParameters
    @validator('currency')
    def transform_currency(cls, v):
        return v.lower()


class ModelCountryTo(BaseModel):
    id: int = Field(alias='i')
    name: str = Field(alias='n')
    country: str = Field(alias='c')


class ModelCityFrom(BaseModel):
    id: int
    name: str
    name_rod: str = Field(alias='nameRd')


class ModelCityTo(BaseModel):
    id: int = Field(alias='i')
    name: str = Field(alias='n')


class ModelTourData(BaseModel):
    offer: ModelOffer
    city_from: ModelCityFrom = Field(alias='dept')
    country_to: ModelCountryTo = Field(alias='t')
    city_to: ModelCityTo = Field(alias='c')

    hotel_id: int = Field(alias='hotelId')
    hotel_name: str = Field(alias='n')
    hotel_name_snake: str = Field(alias='h')
    hotel_stars: str = Field(alias='s')
    image: str = Field(alias='f')

    op_src_json: str = None
    op_full_hotel_name: str = None
    op_country_name: str = None
    op_city_to_name: str = None
    op_city_from_name: str = None
    op_location_from_string: str = None
    op_food_string: str = None
    op_operator_name: str = None
    op_date_duration_string: str = None

    op_promo: bool = None
    op_price: str = None
    op_price_uah: str = None
    op_price_uah_one: str = None
    op_price_usd: Optional[str] = None
    op_price_euro: Optional[str] = None

    op_port_from_name: str = None
    op_port_to_name: str = None

    op_link: str = None

    op_update = datetime.now()

    # noinspection PyMethodParameters
    @validator('image')
    def transform_image(cls, v):
        return f'https://newimg.otpusk.com/2/400x300/{v}'

    # noinspection PyMethodParameters
    @validator('hotel_stars')
    def transform_hotel_stars(cls, v):
        return f'{v}*'


class ModelTour:
    def __init__(self, lang_id_input: int, input_data: dict):
        self.input_data: dict = input_data
        self.lang_id = lang_id_input
        self.lang = LANGS[self.lang_id]
        self.data: Optional[ModelTourData] = None

    def fill_fields(self):
        self.data.op_full_hotel_name = "{} {}".format(self.data.hotel_name, self.data.hotel_stars)

        self.data.op_country_name = get_country_name(country_id=self.data.country_to.id, lang_id=self.lang_id)
        self.data.op_city_to_name = get_city_name(city_id=self.data.city_to.id, lang_id=self.lang_id)
        self.data.op_city_from_name = get_from_city_name(city_from_id=self.data.city_from.id, lang_id=self.lang_id)
        self.data.op_operator_name = get_operators(operator_id=self.data.offer.operator_id, lang_id=self.lang_id)

        self.data.op_location_from_string = location_from(
            STATIC_DATA[self.lang]['transport'][self.data.offer.transport_type],
            self.data.op_city_from_name, lang=self.lang)
        self.data.op_food_string = STATIC_DATA[self.lang]['food'][self.data.offer.food].title()
        self.data.op_date_duration_string = date_duration(self.data.offer.tour_start,
                                                          self.data.offer.length, lang=self.lang)

        self.data.op_promo = True if self.data.offer.promo == 'promo' else False
        self.data.op_price = decimal2str_with_space(math.ceil(self.data.offer.sum_currency))
        self.data.op_price_uah = decimal2str_with_space(math.ceil(self.data.offer.sum_uah))
        self.data.op_price_uah_one = decimal2str_with_space(math.ceil(self.data.offer.sum_uah / 2))
        self.data.op_price_usd = self.data.offer.sum_currency if self.data.offer.currency == 'usd' else None
        self.data.op_price_euro = self.data.offer.sum_currency if self.data.offer.currency == 'usd' == 'eur' else None

        self.data.op_src_json = json.dumps(self.input_data)

        if len(self.data.offer.transport.transport_from) > 0:
            transport = self.data.offer.transport.transport_from[0]
            if len(transport.port_from) >= 3:
                city = get_iata_city(iata_code=transport.port_from[:3], lang_id=self.lang_id)
                if city is not None:
                    self.data.op_port_from_name = city

            if len(transport.port_to) >= 3:
                city = get_iata_city(iata_code=transport.port_to[:3], lang_id=self.lang_id)
                if city is not None:
                    self.data.op_port_to_name = city

    def run(self):
        try:
            self.data = ModelTourData(**self.input_data)
        except ValidationError as error_msg:
            raise ValidationError(error_msg)
        else:
            self.fill_fields()


if __name__ == '__main__':
    pprint(hotel_min_offer)
    exit(1)
    lang_id = LANGS.index('ukr')

    try:
        tour = ModelTour(lang_id_input=lang_id, input_data=hotel_min_offer)
        tour.run()
    except ValidationError as e:
        print(e.json())
        exit(1)
    else:
        pprint(tour.data.dict())
