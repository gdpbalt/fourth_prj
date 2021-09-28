import re
import time
from pprint import pprint
from typing import Optional

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

NUM_POSTS_PER_PAGE = 5


class TAPostData(BaseModel):
    id: int
    author: str
    date: str
    rate: float
    title: str
    text: str


class TAReviewsData(BaseModel):
    url: str
    time: float
    number: int
    name_full: str
    name: str
    stars: int
    posts: list[TAPostData]


hotel_data = dict()


def ta_parse_hotel_name_full(response: BeautifulSoup) -> Optional[str]:
    tag = response.find("h1", class_=["header", "heading", "masthead", "masthead_h1"])
    if not tag:
        print("Get hotel name not found")
        return
    return tag.text


def ta_parse_hotel_name(text: str) -> Optional[str]:
    text = re.sub(r'Отель', '', text).strip()
    names = text.split(",")
    if not names:
        return text

    text = names[0]
    text = re.sub(r'\d+\*', '', text).strip()

    return text


def ta_parse_hotel_stars(text: str) -> Optional[int]:
    results = re.findall(r'\s(\d+)\*', text)
    if not results:
        print(f'Not found stars in input string {text}')
        return

    try:
        number = int(results[0])
    except Exception as e:
        print(f"Can't convert str {results[0]} to int. ", e)
        return

    return number


def ta_parse_number_reviews(response: BeautifulSoup) -> Optional[int]:
    tag = response.find("span", class_="ui_bubble_rating")
    if not tag or tag.is_empty_element:
        print("Get number of reviews not found or empty")
        return

    text = tag.next.text
    if not text:
        print('Number of reviews not found')
        return

    text = re.sub(r'\s', '', text)
    results = re.findall(r'(\d+)', text)
    if not results:
        print(f'Not found numbers in input string {text}')
        return

    try:
        number = int(results[0])
    except Exception as e:
        print(f"Can't convert str {results[0]} to int. ", e)
        return

    return number


def ta_parse_post_index(response: BeautifulSoup) -> Optional[int]:
    tag = response.find("div", attrs={"data-reviewid": True})
    if not tag:
        print("Get post index is wrong")
        return

    try:
        number = int(tag.attrs["data-reviewid"])
    except Exception as e:
        print(f"Can't convert str {tag.attrs['data-reviewid']} to int. ", e)
        return
    return number


def ta_parse_post_author(response: BeautifulSoup) -> Optional[str]:
    tag = response.find("a", class_="ui_header_link bPvDb")
    if not tag:
        print("Get author name is wrong")
        return
    return tag.text


def ta_parse_post_date(response: BeautifulSoup) -> Optional[str]:
    tag = response.find("div", class_="bcaHz")
    if not tag:
        print("Get post date is wrong")
        return

    text = tag.text
    results = text.split("написал(а) отзыв")
    if (num := len(results)) > 0:
        return results[num - 1].strip()


def ta_parse_post_rate(response: BeautifulSoup) -> Optional[float]:
    tag = response.find("span", class_="ui_bubble_rating")
    if not tag:
        print("Get post rate is wrong")
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
        print("Post rating not found", e)
        return
    return number / 10


def ta_parse_post_title(response: BeautifulSoup) -> Optional[str]:
    tag = response.find("div", attrs={"data-test-target": "review-title"})
    if not tag:
        print("Get post title is wrong")
        return
    return tag.text


def ta_parse_post_text(response: BeautifulSoup) -> Optional[str]:
    tag = response.find("q", class_="XllAv H4 _a")
    if not tag:
        print("Get post content is wrong")
        return
    return tag.text


def get_html_content_request(url: str) -> Optional[str]:
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
        "cache-control": "max-age=0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " +
                      "Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
    }
    r = requests.get(url, headers=headers)  # verify=False

    if r.status_code != 200:
        print('status code:', r.status_code)
        return

    return r.text


def get_html_content(url: str, usecache: bool = False) -> Optional[BeautifulSoup]:
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

    return BeautifulSoup(html, 'html.parser')


def parse_general(response: BeautifulSoup) -> None:
    if not response:
        print("Response is empty")
        return

    if (value := ta_parse_number_reviews(response)) is None:
        print("number of reviews not found")
        return
    hotel_data['number'] = value

    if (value := ta_parse_hotel_name_full(response)) is None:
        print("hotel name not found")
        return
    hotel_data['name_full'] = value

    if (value := ta_parse_hotel_name(hotel_data['name_full'])) is None:
        print("hotel name not found")
        return
    hotel_data['name'] = value

    if (value := ta_parse_hotel_stars(hotel_data['name_full'])) is None:
        print("hotel stars not found")
        return
    hotel_data['stars'] = value


def parse_posts(response: BeautifulSoup) -> None:
    if not response:
        print("Response is empty")
        return

    tags = response.find_all('div', class_="cWwQK MC R2 Gi z Z BB dXjiy")
    hotel_data['posts'] = list()
    for idx, review in enumerate(tags):
        post = dict()

        if (value := ta_parse_post_index(review)) is None:
            print("review index not found")
            return
        post['id'] = value

        if (value := ta_parse_post_author(review)) is None:
            print("author name not found")
            return
        post['author'] = value

        if (value := ta_parse_post_date(review)) is None:
            print("post date not found")
            return
        post['date'] = value

        if (value := ta_parse_post_rate(review)) is None:
            print("post rate not found")
            return
        post['rate'] = value

        if (value := ta_parse_post_title(review)) is None:
            print("post title not found")
            return
        post['title'] = value

        if (value := ta_parse_post_text(review)) is None:
            print("post content not found")
            return
        post['text'] = value

        hotel_data['posts'].append(post)


def parse_tripadvisor(url: str, usecache: bool = False) -> TAReviewsData:
    time_start = time.time()

    content = get_html_content(URL, usecache=usecache)
    parse_general(content)
    parse_posts(content)

    hotel_data['url'] = url
    hotel_data['time'] = time.time() - time_start

    data = TAReviewsData(**hotel_data)
    return data


# URL = 'https://www.tripadvisor.ru/' + \
#       'Hotel_Review-g562819-d289642-Reviews-Hotel_Caserio-Playa_del_Ingles_Maspalomas_Gran_Canaria_Canary_Islands.html'
# URL = 'https://www.tripadvisor.ru/' + \
#       'Hotel_Review-g297969-d508059-Reviews-Rixos_Premium_Tekirova-Tekirova_Kemer_Turkish_Mediterranean_Coast.html'
URL = "https://www.tripadvisor.ru/" \
      + "Hotel_Review-g297969-d1166801-Reviews-Pirate_s_Beach_Club-Tekirova_Kemer_Turkish_Mediterranean_Coast.html"

if __name__ == "__main__":
    tripadvisor = parse_tripadvisor(url=URL, usecache=True)

    # print(tripadvisor.json(ensure_ascii=False, indent=4))
    pprint(tripadvisor.dict())
    print("Ok")
