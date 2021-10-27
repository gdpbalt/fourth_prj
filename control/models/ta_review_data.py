import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class TAPostData(BaseModel):
    id: int
    author: Optional[str]
    avatar: Optional[str]
    author_geo: Optional[str] = Field(alias="authorGeo")
    date: Optional[str]
    date_published: datetime.date = Field(alias="datePublished")
    date_stay: Optional[str] = Field(alias="dateStay")
    rate: Optional[float]
    rate_text: Optional[str] = Field(alias="rateText")
    title: Optional[str]
    text_brief: str = Field(alias="textBrief")
    text_full: str = Field(alias="textFull")

    # noinspection PyMethodParameters
    @validator('date_published')
    def transform_date_published(cls, v):
        return v.isoformat()


class TAReviewsData(BaseModel):
    time: float
    number: int
    name_full: str = Field(alias="nameFull")
    name: str
    stars: Optional[float]
    rate: float
    page: int
    posts: list[TAPostData]
    updated: datetime.datetime

    # noinspection PyMethodParameters
    @validator('updated')
    def transform_updated(cls, v):
        return v.isoformat(timespec="seconds")
