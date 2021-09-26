import re
from pprint import pprint
from typing import Optional

import requests
from bs4 import BeautifulSoup

hotel_data = dict()


def get_html_content(url):
    filename = r'C:\Projects\fourth_prj\temp.html'
    text = ''
    try:
        with open('temp.html', 'r', encoding='utf8') as f:
            print(f"Read content from {filename}")
            for line in f:
                text += line
    except IOError:
        print(f"Read content from {url}")
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'}
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            print('status code:', r.status_code)
            exit(1)
        text = r.text

        with open(filename, 'w+', encoding='utf8') as f:
            f.write(text)

    return BeautifulSoup(text, 'html.parser')


def parse_review_count(response: BeautifulSoup) -> Optional[int]:
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


def parse_hotel_name(response: BeautifulSoup) -> Optional[str]:
    tag = response.find("h1", class_=["header", "heading", "masthead", "masthead_h1"])
    if not tag:
        print("Get hotel name not found")
        return

    text = re.sub(r'Отель', '', tag.text).strip()
    names = text.split(",")
    if not names:
        return text
    return names[0]


def parse(response: BeautifulSoup) -> None:
    if not response:
        print("Response is empty")
        return

    if (value := parse_review_count(response)) is None:
        print("number of reviews not found")
        return
    hotel_data['num_reviews'] = value

    if (value := parse_hotel_name(response)) is None:
        print("hotel name not found")
        return
    hotel_data['hotel_name'] = value


def get_review_post_index(response: BeautifulSoup) -> Optional[int]:
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


def get_review_post_author(response: BeautifulSoup) -> Optional[str]:
    tag = response.find("a", class_="ui_header_link bPvDb")
    if not tag:
        print("Get author name is wrong")
        return
    return tag.text


def get_review_post_date(response: BeautifulSoup) -> Optional[str]:
    tag = response.find("div", class_="bcaHz")
    if not tag:
        print("Get post date is wrong")
        return

    text = tag.text
    results = text.split("написал(а) отзыв")
    if (num := len(results)) > 0:
        return results[num-1].strip()


def get_review_post_rate(response: BeautifulSoup) -> Optional[int]:
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
    return value


def get_review_post_title(response: BeautifulSoup) -> Optional[str]:
    tag = response.find("div", attrs={"data-test-target": "review-title"})
    if not tag:
        print("Get post title is wrong")
        return
    return tag.text


def get_review_post_text(response: BeautifulSoup) -> Optional[str]:
    tag = response.find("q", class_="XllAv H4 _a")
    if not tag:
        print("Get post content is wrong")
        return
    return tag.text


def parse_reviews(response: BeautifulSoup) -> None:
    if not response:
        print("Response is empty")
        return

    tags = response.find_all('div', class_="cWwQK MC R2 Gi z Z BB dXjiy")
    for idx, review in enumerate(tags):
        if (index := get_review_post_index(review)) is None:
            print("review index not found")
            return
        hotel_data[index] = dict()

        if (value := get_review_post_author(review)) is None:
            print("author name not found")
            return
        hotel_data[index]['review_post_author'] = value

        if (value := get_review_post_date(review)) is None:
            print("post date not found")
            return
        hotel_data[index]['review_post_date'] = value

        if (value := get_review_post_rate(review)) is None:
            print("post rate not found")
            return
        hotel_data[index]['review_post_rate'] = value

        if (value := get_review_post_title(review)) is None:
            print("post title not found")
            return
        hotel_data[index]['review_post_title'] = value

        if (value := get_review_post_text(review)) is None:
            print("post content not found")
            return
        hotel_data[index]['review_post_text'] = value


# URL = 'https://www.tripadvisor.ru/' + \
#       'Hotel_Review-g562819-d289642-Reviews-Hotel_Caserio-Playa_del_Ingles_Maspalomas_Gran_Canaria_Canary_Islands.html'
URL = 'https://www.tripadvisor.ru/' + \
      'Hotel_Review-g297969-d508059-Reviews-Rixos_Premium_Tekirova-Tekirova_Kemer_Turkish_Mediterranean_Coast.html'
# URL = "https://www.tripadvisor.ru/" \
#       + "Hotel_Review-g297969-d1166801-Reviews-Pirate_s_Beach_Club-Tekirova_Kemer_Turkish_Mediterranean_Coast.html"

bs = get_html_content(URL)
parse(bs)
parse_reviews(bs)
pprint(hotel_data)
print("Ok")
