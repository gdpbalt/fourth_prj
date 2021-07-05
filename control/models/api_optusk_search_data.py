from datetime import date, datetime
from typing import Optional, Union

from pydantic import BaseModel, Field, validator


class ModelTransferData(BaseModel):
    begin: datetime = None
    end: datetime = None
    port_from: str = Field(alias='portFr', default=None)
    port_to: str = Field(alias='portTo', default=None)


class ModelTransferFromTo(BaseModel):
    transport_from: list[ModelTransferData] = Field(alias='from')
    transport_to: list[ModelTransferData] = Field(alias='to')


class ModelOffer(BaseModel):
    tour_api_id: int = Field(alias='i')
    tour_start: date = Field(alias='d')

    transport: Union[ModelTransferFromTo, dict] = Field(alias='to')
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

    # noinspection PyMethodParameters
    @validator('transport')
    def transform_transport(cls, v):
        if isinstance(v, list):
            return dict()
        return v


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


class ModelLocation(BaseModel):
    lat: float = Field(alias='a')
    lng: float = Field(alias='o')
    zoom: int = Field(alias='z')


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
    location: ModelLocation = Field(alias='g')

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

    op_port_to_iata: str = None
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
