from typing import Optional

from pydantic import BaseModel


class TAPostData(BaseModel):
    id: int
    author: Optional[str]
    author_geo: Optional[str]
    date: Optional[str]
    date_stay: Optional[str]
    rate: Optional[float]
    rate_text: Optional[str]
    title: Optional[str]
    text_brief: str
    text_second: Optional[str]
    text_full: str


class TAReviewsData(BaseModel):
    # url: str
    time: float
    number: int
    name_full: str
    name: str
    stars: Optional[int]
    rate: float
    page: int
    posts: list[TAPostData]
