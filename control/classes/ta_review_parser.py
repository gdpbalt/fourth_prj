import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup
from pydantic import ValidationError

from control import app
from control.models.ta_review_data import TAReviewsData
from control.utils.ta_parse import ta_parse_number_reviews, ta_parse_rate, ta_parse_hotel_name_full, \
    ta_parse_hotel_name, ta_parse_hotel_stars, ta_parse_post_index, ta_parse_post_author, ta_parse_post_author_geo, \
    ta_parse_post_date, ta_parse_post_date_stay, ta_parse_post_rate, ta_parse_post_title, ta_parse_post_text


class TAParseExeption(Exception):
    pass


class TAParse:
    NUM_POSTS_PER_PAGE = 5
    RATE_TEXT = [None, "Ужасно", "Плохо", "Неплохо", "Очень хорошо", "Отлично"]

    def __init__(self, url: str, page: int = 0, usecache: bool = False) -> None:
        self.url = url
        self.page = page
        self.usecache = usecache

        self.data = dict()

    @staticmethod
    def get_html_content_request(url: str) -> Optional[str]:
        header = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " +
                          "Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
        }
        try:
            app.logger.debug(f'GET {url}')
            r = requests.get(url, headers=header)
        except Exception as e:
            msg = f'Network connection error'
            app.logger.error(f"{msg}. {e}")
            return

        if r.status_code != requests.codes.ok:
            msg = f'Network connection error'
            app.logger.error(f'{msg}. Answer={r.status_code}')
            return

        return r.text

    def get_html_content(self, url: str, usecache: bool = False) -> Optional[str]:
        filename = r'C:\Projects\fourth_prj\temp.html'
        html = ''

        is_need_to_request = True
        if usecache:
            try:
                with open('temp.html', 'r', encoding='utf8') as f:
                    print(f"Read content from {filename}")
                    for line in f:
                        html += line
            except IOError:
                is_need_to_request = True
            else:
                is_need_to_request = False

        if is_need_to_request:
            print(f"Read content from {url}")
            html = self.get_html_content_request(url)
            if html is None:
                return
            else:
                with open(filename, 'w+', encoding='utf8') as f:
                    f.write(html)

        return html

    def parse_general(self, response: BeautifulSoup) -> None:
        key = 'number'
        self.data[key] = ta_parse_number_reviews(key, response)

        key = 'rate'
        self.data[key] = ta_parse_rate(key, response)

        key = 'name_full'
        self.data[key] = ta_parse_hotel_name_full(key, response)

        key = 'name'
        self.data[key] = ta_parse_hotel_name(key, self.data['name_full'])

        key = 'stars'
        self.data[key] = ta_parse_hotel_stars(key, self.data['name_full'])

    def parse_posts(self, response: BeautifulSoup) -> None:
        list_of_posts = list()
        tags = response.find_all('div', class_="cWwQK MC R2 Gi z Z BB dXjiy")
        for idx, review in enumerate(tags):
            post = dict()

            key = 'id'
            post[key] = ta_parse_post_index(key, review)

            author_block = review.find("div", class_="xMxrO")
            if author_block is not None:
                key = 'author'
                post[key] = ta_parse_post_author(key, author_block)

                key = 'author_geo'
                post[key] = ta_parse_post_author_geo(key, author_block)

                key = 'date'
                post[key] = ta_parse_post_date(key, author_block)

            key = 'date_stay'
            post[key] = ta_parse_post_date_stay(key, review)

            key = 'rate'
            post[key] = ta_parse_post_rate(key, review)

            key = 'title'
            post[key] = ta_parse_post_title(key, review)

            text_list = ta_parse_post_text(key, review)
            if len(text_list) >= 1:
                post["text_second"] = ''
                for key, value in enumerate(text_list):
                    if key == 0:
                        post["text_brief"] = value
                    elif key == 1:
                        post["text_second"] = value
                    else:
                        break
                post["text_full"] = post["text_brief"] + post["text_second"]

            list_of_posts.append(post)

        self.data['posts'] = sorted(list_of_posts, key=lambda x: x['id'], reverse=True)

    def run(self) -> TAReviewsData:
        time_start = time.time()

        if self.page > 1:
            pattern = '-Reviews-'
            _url = re.sub(pattern, "{}or{}-".format(pattern, (self.page - 1) * self.NUM_POSTS_PER_PAGE), self.url)
        else:
            _url = self.url

        if (html := self.get_html_content(_url, usecache=self.usecache)) is None:
            raise TAParseExeption(f"Error get data from {_url}")

        if (bs := BeautifulSoup(html, 'html.parser')) is None:
            raise TAParseExeption(f"Error parse data from {_url}")

        self.parse_general(bs)
        self.parse_posts(bs)

        self.data['url'] = _url
        self.data['time'] = time.time() - time_start
        for idx, post in enumerate(self.data["posts"]):
            rate = int(post["rate"])
            if 5 >= rate >= 1:
                self.data["posts"][idx]["rate_text"] = self.RATE_TEXT[rate]
            else:
                self.data["posts"][idx]["rate_text"] = None

        try:
            data = TAReviewsData(**self.data)
        except ValidationError as e:
            raise TAParseExeption(f"Error parse data from {_url}. Validation error ({e})")
        return data


if __name__ == "__main__":
    # URL = 'https://www.tripadvisor.ru/' + \
    #       'Hotel_Review-g562819-d289642-Reviews-' + \
    #       'Hotel_Caserio-Playa_del_Ingles_Maspalomas_Gran_Canaria_Canary_Islands.html'
    # URL = 'https://www.tripadvisor.ru/' + \
    #       'Hotel_Review-g297969-d508059-Reviews-' + \
    #       'Rixos_Premium_Tekirova-Tekirova_Kemer_Turkish_Mediterranean_Coast.html'
    URL = "https://www.tripadvisor.ru/" \
          + "Hotel_Review-g297969-d1166801-Reviews-" + \
          "Pirate_s_Beach_Club-Tekirova_Kemer_Turkish_Mediterranean_Coast.html"

    ta = TAParse(url=URL, page=0, usecache=False)
    try:
        tripadvisor = ta.run()
    except Exception as error:
        print(f"Error get data ({error})")
    else:
        arr = tripadvisor.dict()

        for arr_key, arr_value in arr.items():
            if arr_key == 'posts':
                continue
            print(f"{arr_key}: {arr_value}")

        for posts in arr['posts']:
            print("-" * 25)
            for arr_key, arr_value in posts.items():
                if arr_key == 'text_second' or arr_key == 'text_full':
                    continue
                print(f"{arr_key}: {arr_value}")
