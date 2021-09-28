import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError

from control import app

NUM_POSTS_PER_PAGE = 5
RATE_TEXT = [None, "Ужасно", "Плохо", "Неплохо", "Очень хорошо", "Отлично"]


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
    url: str
    time: float
    number: int
    name_full: str
    name: str
    stars: int
    rate: float
    posts: list[TAPostData]


class TAParseExeption(Exception):
    pass


hotel_data = dict()


def ta_parse_hotel_name_full(key: str, response: BeautifulSoup) -> Optional[str]:
    tag = response.find("h1", class_=["header heading masthead masthead_h1"])
    if not tag:
        app.logger.error(f"{key}: not found")
        return
    return tag.text


def ta_parse_hotel_name(key: str, text: str) -> Optional[str]:
    text = re.sub(r'Отель', '', text).strip()
    names = text.split(",")
    if not names:
        return text

    text = names[0]
    text = re.sub(r'\d+\*', '', text).strip()

    return text


def ta_parse_hotel_stars(key: str, text: str) -> Optional[int]:
    results = re.findall(r'\s(\d+)\*', text)
    if not results:
        app.logger.error(f"{key}: not found")
        return

    try:
        number = int(results[0])
    except Exception as e:
        app.logger.error(f"{key}: can't convert to int ({e})")
        return

    return number


def ta_parse_number_reviews(key: str, response: BeautifulSoup) -> Optional[int]:
    tag = response.find("span", class_="btQSs q Wi z Wc")
    if not tag or tag.is_empty_element:
        app.logger.error(f"{key}: not found or empty")
        return

    text_orig = tag.next.text
    if not text_orig:
        app.logger.error(f"{key}: not found")
        return

    text = re.sub(r'\s', '', text_orig)
    results = re.findall(r'^(\d+)', text)
    if not results:
        app.logger.error(f"{key}: numbers not found in input string {text_orig}")
        return

    try:
        number = int(results[0])
    except Exception as e:
        app.logger.error(f"{key}: can't convert to int ({e})")
        return

    return number


def ta_parse_rate(key: str, response: BeautifulSoup) -> Optional[float]:
    tag = response.find("span", class_="bvcwU P")
    if not tag:
        app.logger.error(f"{key}: not found")
        return

    value = tag.text
    value = value.replace(",", ".")

    try:
        number = float(value)
    except Exception as e:
        app.logger.error(f"{key}: can't convert to float ({e})")
        return
    return number


def ta_parse_post_index(key: str, response: BeautifulSoup) -> Optional[int]:
    tag = response.find("div", attrs={"data-reviewid": True})
    if not tag:
        app.logger.error(f"{key}: not found")
        return

    try:
        number = int(tag.attrs["data-reviewid"])
    except Exception as e:
        app.logger.error(f"{key}: can't convert to int ({e})")
        return
    return number


def ta_parse_post_author(key: str, response: BeautifulSoup) -> Optional[str]:
    tag = response.find("a", class_="ui_header_link bPvDb")
    if not tag:
        app.logger.error(f"{key}: not found")
        return
    return tag.text


def ta_parse_post_author_geo(key: str, response: BeautifulSoup) -> Optional[str]:
    tag = response.find("span", class_="fSiLz")
    if not tag:
        return
    return tag.text


def ta_parse_post_date(key: str, response: BeautifulSoup) -> Optional[str]:
    tag = response.find("div", class_="bcaHz")
    if not tag:
        app.logger.error(f"{key}: not found")
        return

    text = tag.text
    search_pattern = "написал(а) отзыв"
    results = text.split(search_pattern)
    if (num := len(results)) == 0:
        app.logger.error(f"{key}: can't find text '{search_pattern}'")
        return
    else:
        return "{} {}".format(search_pattern, results[num - 1].strip())


def ta_parse_post_date_stay(key: str, response: BeautifulSoup) -> Optional[str]:
    tag = response.find("span", class_="euPKI _R Me S4 H3")
    if not tag:
        app.logger.error(f"{key}: not found")
        return

    pattern = "Дата пребывания:"
    text = re.sub(pattern, "", tag.text).strip()

    return text


def ta_parse_post_rate(key: str, response: BeautifulSoup) -> Optional[float]:
    tag = response.find("span", class_="ui_bubble_rating")
    if not tag:
        app.logger.error(f"{key}: not found")
        return

    value = None
    for name in tag.attrs["class"]:
        result = re.findall(r"^bubble_(\d+)", name)
        if result:
            value = result[0]
            break

    try:
        number = int(value)
    except Exception as e:
        app.logger.error(f"{key}: can't convert to int ({e})")
        return
    return number / 10


def ta_parse_post_title(key: str, response: BeautifulSoup) -> Optional[str]:
    tag = response.find("div", class_="fpMxB MC _S b S6 H5 _a")
    if not tag:
        app.logger.error(f"{key}: not found")
        return
    return tag.text


def ta_parse_post_text(key: str, response: BeautifulSoup) -> list:
    texts = list()

    tag = response.find("q", class_="XllAv H4 _a")
    if not tag:
        app.logger.error(f"{key}: not found")
        return texts

    tags = tag.find_all("span")
    for key, tag in enumerate(tags):
        if key > 1:
            break
        texts.append(tag.text)

    return texts


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


def get_html_content(url: str, usecache: bool = False) -> Optional[str]:
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
        html = get_html_content_request(url)
        if html is None:
            return
        else:
            with open(filename, 'w+', encoding='utf8') as f:
                f.write(html)

    return html


def parse_general(response: BeautifulSoup) -> None:
    key = 'number'
    hotel_data[key] = ta_parse_number_reviews(key, response)

    key = 'rate'
    hotel_data[key] = ta_parse_rate(key, response)

    key = 'name_full'
    hotel_data[key] = ta_parse_hotel_name_full(key, response)

    key = 'name'
    hotel_data[key] = ta_parse_hotel_name(key, hotel_data['name_full'])

    key = 'stars'
    hotel_data[key] = ta_parse_hotel_stars(key, hotel_data['name_full'])


def parse_posts(response: BeautifulSoup) -> None:
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

    hotel_data['posts'] = sorted(list_of_posts, key=lambda x: x['id'], reverse=True)


def parse_tripadvisor(url: str, page: int = 0, usecache: bool = False) -> TAReviewsData:
    time_start = time.time()

    if page > 1:
        pattern = '-Reviews-'
        _url = re.sub(pattern, "{}or{}-".format(pattern, (page-1)*NUM_POSTS_PER_PAGE), url)
    else:
        _url = url

    if (html := get_html_content(_url, usecache=usecache)) is None:
        raise TAParseExeption(f"Error get data from {_url}")

    if (bs := BeautifulSoup(html, 'html.parser')) is None:
        raise TAParseExeption(f"Error parse data from {_url}")

    parse_general(bs)
    parse_posts(bs)

    hotel_data['url'] = _url
    hotel_data['time'] = time.time() - time_start
    for idx, post in enumerate(hotel_data["posts"]):
        rate = int(post["rate"])
        if 5 >= rate >= 1:
            hotel_data["posts"][idx]["rate_text"] = RATE_TEXT[rate]
        else:
            hotel_data["posts"][idx]["rate_text"] = None

    try:
        data = TAReviewsData(**hotel_data)
    except ValidationError as e:
        raise TAParseExeption(f"Error parse data from {_url}. Validation error ({e})")
    return data


# URL = 'https://www.tripadvisor.ru/' + \
#       'Hotel_Review-g562819-d289642-Reviews-Hotel_Caserio-Playa_del_Ingles_Maspalomas_Gran_Canaria_Canary_Islands.html'
# URL = 'https://www.tripadvisor.ru/' + \
#       'Hotel_Review-g297969-d508059-Reviews-Rixos_Premium_Tekirova-Tekirova_Kemer_Turkish_Mediterranean_Coast.html'
URL = "https://www.tripadvisor.ru/" \
      + "Hotel_Review-g297969-d1166801-Reviews-Pirate_s_Beach_Club-Tekirova_Kemer_Turkish_Mediterranean_Coast.html"

if __name__ == "__main__":
    try:
        tripadvisor = parse_tripadvisor(url=URL, page=10, usecache=False)
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
