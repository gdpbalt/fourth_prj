import datetime
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup
from pydantic import ValidationError
from sqlalchemy import exc

from control import app, OtpuskHotelTACache, db
from control.classes.ta_review_pattern import TAParsePattern
from control.models.ta_review_data import TAReviewsData
from control.settings import TRIPADVISER_GET_CONTENT_FROM_SITE_AFTER_NETWORK_ERROR_MINUTES, \
    TRIPADVISER_GET_CONTENT_FROM_SITE_AFTER_PARSE_ERROR_MINUTES, TRIPADVISER_GET_CONTENT_FROM_SITE_AFTER_MINUTES


class TAParseExeption(Exception):
    pass


class TAParse(TAParsePattern):
    NUM_POSTS_PER_PAGE = 5
    RATE_TEXT = [None, "Ужасно", "Плохо", "Неплохо", "Очень хорошо", "Отлично"]

    def __init__(self, hotel_id: int, url: str, page: int = 0) -> None:
        self.url = url
        self.page = page
        self.hotel_id = hotel_id

        self.data = dict()

    @staticmethod
    def get_html_content(url: str) -> Optional[str]:
        header = {
            "Connection": "Keep-Alive",
            "Accept-Encoding": "identity",
            "User-Agent": "Wget/1.19.4 (linux-gnu)",
        }
        try:
            app.logger.debug(f'GET {url}')
            r = requests.get(url, headers=header, timeout=10)
        except Exception as e:
            msg = f'Network connection error'
            app.logger.error(f"{msg}. {e}")
            return

        if r.status_code != requests.codes.ok:
            msg = f'Network connection error'
            app.logger.error(f'{msg}. Answer={r.status_code}')
            return

        return r.text

    def parse_general(self, response: BeautifulSoup) -> None:
        key = 'number'
        self.data[key] = self.ta_parse_number_reviews(key, response)

        key = 'rate'
        self.data[key] = self.ta_parse_rate(key, response)

        key = 'page'
        self.data[key] = self.ta_parse_page(key, response)

        key = 'nameFull'
        self.data[key] = self.ta_parse_hotel_name_full(key, response)

        key = 'name'
        self.data[key] = self.ta_parse_hotel_name(key, self.data['nameFull'])

        key = 'stars'
        self.data[key] = self.ta_parse_hotel_stars(key, self.data['nameFull'])

    def parse_posts(self, response: BeautifulSoup) -> None:
        list_of_posts = list()
        tags = response.find_all('div', class_="cWwQK MC R2 Gi z Z BB dXjiy")
        for idx, review in enumerate(tags):
            post = dict()

            key = 'id'
            post[key] = self.ta_parse_post_index(key, review)

            author_block = review.find("div", class_="xMxrO")
            if author_block is not None:
                key = 'author'
                post[key] = self.ta_parse_post_author(key, author_block)

                key = 'authorGeo'
                post[key] = self.ta_parse_post_author_geo(key, author_block)

                key = 'date'
                post[key] = self.ta_parse_post_date(key, author_block)

            key = 'dateStay'
            post[key] = self.ta_parse_post_date_stay(key, review)

            key = 'rate'
            post[key] = self.ta_parse_post_rate(key, review)

            rate = int(post['rate'])
            if 5 >= rate >= 1:
                post["rateText"] = self.RATE_TEXT[rate]
            else:
                post["rateText"] = None

            key = 'title'
            post[key] = self.ta_parse_post_title(key, review)

            text_list = self.ta_parse_post_text(key, review)
            if len(text_list) >= 1:
                post["textSecond"] = ''
                for key, value in enumerate(text_list):
                    if key == 0:
                        post["textBrief"] = value
                    elif key == 1:
                        post["textSecond"] = value
                    else:
                        break
                post["textFull"] = post["textBrief"] + post["textSecond"]

            list_of_posts.append(post)

        self.data['posts'] = sorted(list_of_posts, key=lambda x: x['id'], reverse=True)

    def convert_url(self, url: str, page: int) -> str:
        if url is None or len(url) == 1:
            raise TAParseExeption(f"Url is too short ({url})")

        new_url = re.sub("tripadvisor.com", "tripadvisor.ru", url)

        if re.match(r"^/Hotel_Review", new_url):
            new_url = r"https://tripadvisor.ru" + new_url

        if re.match(r"^http.*:/+Hotel_Review", new_url):
            new_url = re.sub(r"http.*:/+Hotel_Review", r"https://tripadvisor.ru/Hotel_Review", url)

        if page > 1:
            pattern = '-Reviews-'
            new_url = re.sub(pattern, "{}or{}-".format(pattern, (page - 1) * self.NUM_POSTS_PER_PAGE), new_url)
        return new_url

    def save2dbase(self, is_error: bool, timeout: int, data: Optional[TAReviewsData] = None) -> None:
        updated = datetime.datetime.now()
        expired = updated + datetime.timedelta(minutes=timeout)
        if is_error:
            content = None
        else:
            content = data.json(by_alias=True)

        result: OtpuskHotelTACache = OtpuskHotelTACache.query.get((self.hotel_id, self.page))
        if result is None:
            result = OtpuskHotelTACache(id=self.hotel_id, page=self.page, content=content,
                                        expired=expired, updated=updated)
            db.session.add(result)
        else:
            result.content = content
            result.expired = expired
            result.updated = updated

        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            msg = f'Error work with database. {e}'
            app.logger.error(msg)
            raise ConnectionError(msg)

    def run(self) -> TAReviewsData:
        time_start = time.time()
        url = self.convert_url(url=self.url, page=self.page)
        self.data['url'] = url

        if (html := self.get_html_content(url=url)) is None:
            self.save2dbase(is_error=True, timeout=TRIPADVISER_GET_CONTENT_FROM_SITE_AFTER_NETWORK_ERROR_MINUTES)
            raise TAParseExeption(f"Error get data from {url}")

        if (bs := BeautifulSoup(html, 'html.parser')) is None:
            self.save2dbase(is_error=True, timeout=TRIPADVISER_GET_CONTENT_FROM_SITE_AFTER_PARSE_ERROR_MINUTES)
            raise TAParseExeption(f"Error parse data from {url}")

        self.parse_general(bs)
        self.parse_posts(bs)

        self.data['time'] = time.time() - time_start
        self.data['updated'] = datetime.datetime.now()
        try:
            data = TAReviewsData(**self.data)
        except ValidationError as e:
            self.save2dbase(is_error=True, timeout=TRIPADVISER_GET_CONTENT_FROM_SITE_AFTER_PARSE_ERROR_MINUTES)
            raise TAParseExeption(f"Error parse data from {url}. Validation error ({e})")
        except Exception as e:
            self.save2dbase(is_error=True, timeout=TRIPADVISER_GET_CONTENT_FROM_SITE_AFTER_PARSE_ERROR_MINUTES)
            raise TAParseExeption(f"Error parse from {url}. Some error occured ({e})")

        self.save2dbase(is_error=False, timeout=TRIPADVISER_GET_CONTENT_FROM_SITE_AFTER_MINUTES, data=data)
        return data


if __name__ == "__main__":
    URL = "https://www.tripadvisor.ru/" \
          + "Hotel_Review-g297969-d1166801-Reviews-" + \
          "Pirate_s_Beach_Club-Tekirova_Kemer_Turkish_Mediterranean_Coast.html"

    ta = TAParse(hotel_id=1, url=URL, page=0)
    try:
        tripadvisor = ta.run()
    except Exception as error:
        print(f"Error get data: {error}")
    else:
        arr = tripadvisor.dict()

        for arr_key, arr_value in arr.items():
            if arr_key == 'posts':
                continue
            print(f"{arr_key}: {arr_value}")

        for posts in arr['posts']:
            print("-" * 25)
            for arr_key, arr_value in posts.items():
                if arr_key == 'textSecond' or arr_key == 'textFull':
                    continue
                print(f"{arr_key}: {arr_value}")
