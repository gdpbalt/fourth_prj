import datetime
import json
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

    HEADER = {
        "Connection": "Keep-Alive",
        "Accept-Encoding": "identity",
        "User-Agent": "Wget/1.19.4 (linux-gnu)",
    }

    def __init__(self, hotel_id: int, url: str, page: int = 0) -> None:
        self.url = url
        self.page = page
        self.hotel_id = hotel_id
        self.logprefix = "Hotel:{}, Page:{}".format(self.hotel_id, self.page)

        self.data = dict()

    def get_html_content(self, url: str) -> Optional[str]:
        try:
            app.logger.debug(f'GET {url}')
            r = requests.get(url, headers=self.HEADER, timeout=10)
        except Exception as e:
            msg = f'Network connection error'
            app.logger.error(f"{self.logprefix}. {msg}. {e}")
            return

        if r.status_code != requests.codes.ok:
            msg = f'Network connection error'
            app.logger.error(f'{self.logprefix}. {msg}. Answer={r.status_code}')
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

    def parse_posts_from_html(self, response: BeautifulSoup) -> None:
        list_of_posts = list()
        tags = response.find_all('div', class_="cWwQK MC R2 Gi z Z BB dXjiy")
        for idx, review in enumerate(tags):
            post = dict()

            key = 'id'
            post[key] = self.ta_parse_post_index(key, review)

            author_block = review.find("div", class_="xMxrO")
            if author_block is not None:
                key = 'authorGeo'
                post[key] = self.ta_parse_post_author_geo(key, author_block)

                key = 'date'
                post[key] = self.ta_parse_post_date(key, author_block)

            key = 'dateStay'
            post[key] = self.ta_parse_post_date_stay(key, review)

            value = self.ta_parse_post_text(key, review)
            if value is not None:
                post["textBrief"] = value
            else:
                post["textBrief"] = ''
            post["textFull"] = post["textBrief"]

            list_of_posts.append(post)

        self.data['posts'] = sorted(list_of_posts, key=lambda x: x['id'], reverse=True)

    @staticmethod
    def get_reviews_from_page_manifest(input_data: dict) -> Optional[list]:
        if not isinstance(input_data, dict):
            return

        result = input_data.get("pageManifest")
        if not isinstance(result, dict):
            return

        result = result.get("urqlCache")
        if not isinstance(result, dict):
            return

        reviews = None
        for review_key in result:
            try:
                reviews = result[review_key]['data']['locations'][0]['reviewListPage']['reviews']
            except KeyError:
                pass

        if isinstance(reviews, list):
            return reviews

    def parse_posts_from_manifest(self, response: BeautifulSoup) -> None:
        tag = response.find('script', text=re.compile('window.__WEB_CONTEXT__'))
        if not tag:
            self.print_error(f"__WEB_CONTEXT__: not found")
            return

        data = tag.text
        data = data.replace("window.__WEB_CONTEXT__=", "")
        data = data.replace('{pageManifest:', '{"pageManifest":')
        data = re.sub(r";\(.*$", "", data)
        page_reviews = self.get_reviews_from_page_manifest(json.loads(data))

        for review in page_reviews:
            if not isinstance(review, dict):
                continue

            index = review.get("id")
            if index is None:
                continue
            index = int(index)

            for ready_post in self.data['posts']:
                if ready_post["id"] == index:
                    break
            else:
                continue

            ready_post["datePublished"] = review.get("publishedDate")
            ready_post["rate"] = review.get("rating")
            ready_post["title"] = review.get("title")
            ready_post["textFull"] = review.get("text")

            rate = int(ready_post['rate'])
            if 5 >= rate >= 1:
                ready_post["rateText"] = self.RATE_TEXT[rate]
            else:
                ready_post["rateText"] = None

            ready_post["author"] = None
            ready_post["avatar"] = None
            try:
                ready_post["author"] = review["userProfile"]["displayName"]
                ready_post["avatar"] = review["userProfile"]["avatar"]["photoSizes"][1]["url"]
            except KeyError:
                pass
            except TypeError:
                pass

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
            content, name = None, None
        else:
            content = data.json(by_alias=True)
            name = data.name

        result: OtpuskHotelTACache = OtpuskHotelTACache.query.get((self.hotel_id, self.page))
        if result is None:
            result = OtpuskHotelTACache(id=self.hotel_id, name=name, page=self.page, content=content,
                                        expired=expired, updated=updated)
            db.session.add(result)
        else:
            result.name = name
            result.content = content
            result.expired = expired
            result.updated = updated

        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            msg = f'{self.logprefix}. Error work with database. {e}'
            app.logger.error(f'{self.logprefix}. Error work with database. {e}')
            raise ConnectionError(msg)

    def run(self) -> TAReviewsData:
        time_start = time.time()
        url = self.convert_url(url=self.url, page=self.page)
        self.data['url'] = url

        if (html := self.get_html_content(url=url)) is None:
            self.save2dbase(is_error=True, timeout=TRIPADVISER_GET_CONTENT_FROM_SITE_AFTER_NETWORK_ERROR_MINUTES)
            raise TAParseExeption(f"{self.logprefix}. Error get data from {url}")

        if (bs := BeautifulSoup(html, 'html.parser')) is None:
            self.save2dbase(is_error=True, timeout=TRIPADVISER_GET_CONTENT_FROM_SITE_AFTER_PARSE_ERROR_MINUTES)
            raise TAParseExeption(f"{self.logprefix}. Error parse data from {url}")

        self.parse_general(bs)
        self.parse_posts_from_html(bs)
        if isinstance(self.data['posts'], list) and len(self.data['posts']) > 0:
            self.parse_posts_from_manifest(bs)

        self.data['time'] = time.time() - time_start
        self.data['updated'] = datetime.datetime.now()
        try:
            data = TAReviewsData(**self.data)
        except ValidationError as e:
            self.save2dbase(is_error=True, timeout=TRIPADVISER_GET_CONTENT_FROM_SITE_AFTER_PARSE_ERROR_MINUTES)
            raise TAParseExeption(f"{self.logprefix}. Error parse data from {url}. Validation error ({e})")
        except Exception as e:
            self.save2dbase(is_error=True, timeout=TRIPADVISER_GET_CONTENT_FROM_SITE_AFTER_PARSE_ERROR_MINUTES)
            raise TAParseExeption(f"{self.logprefix}. Error parse from {url}. Some error occured ({e})")

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
