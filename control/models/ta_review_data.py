import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class TAPostData(BaseModel):
    id: int
    author: Optional[str]
    author_geo: Optional[str] = Field(alias="authorGeo")
    date: Optional[str]
    date_stay: Optional[str] = Field(alias="dateStay")
    rate: Optional[float]
    rate_text: Optional[str] = Field(alias="rateText")
    title: Optional[str]
    text_brief: str = Field(alias="textBrief")
    text_second: Optional[str] = Field(alias="textSecond")
    text_full: str = Field(alias="textFull")


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
    def transform_image(cls, v):
        return v.isoformat(timespec="seconds")
