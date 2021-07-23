from typing import Union

from pydantic import BaseModel, Field, validator


class PayClientAdressData(BaseModel):
    region: str
    city: str
    street: str
    house: str
    appartment: str
    zip: str


class PayClientData(BaseModel):
    name: str
    adress: PayClientAdressData
    email: str
    phone: str


class PayPassportData(BaseModel):
    series: str
    number: str
    name: str
    sur_name: str = Field(alias='surName')
    phone: str
    country: str
    ended: str
    birthday: str
    issue: str


class PayPassportsData(BaseModel):
    adults: list[PayPassportData]
    child: list[PayPassportData]


class PayOfferData(BaseModel):
    id: str
    url: str


class PaymentData(BaseModel):
    type: str
    amount: int
    currency: str
    createdDate: int
    transactionStatus: str
    reason: str


class PayBeforeData(BaseModel):
    advert: str
    without_discount: bool = Field(alias='withoutDiscount')
    manager: str
    contest: str = Field(alias='contest1')
    passports: Union[PayPassportsData, dict]
    client: PayClientData
    offer: PayOfferData
    payment: Union[PaymentData, dict] = Field(default=dict())

    # noinspection PyMethodParameters
    @validator('payment')
    def transform_payment(cls, v):
        if isinstance(v, list):
            return dict()
        return v
