import json
import re
from pprint import pprint
from typing import Optional

import requests
from bs4 import BeautifulSoup

# https://stackoverflow.com/questions/56682371/scraping-a-website-with-data-hidden-under-read-more
# https://control.antonivtours.com/api/review?hotelId=27766&access_token=298e9-774cd-1118a-5ccb7-fc8c6&page=2
HEADER = {
    "Connection": "Keep-Alive",
    "Accept-Encoding": "identity",
    "User-Agent": "Wget/1.19.4 (linux-gnu)",
}

URL = "https://www.tripadvisor.ru/Hotel_Review-g303855-d1858675-Reviews-or5-Cleopatra_Luxury_Resort_Sharm_El_Sheikh-Nabq_Bay_Sharm_El_Sheikh_South_Sinai_Red_.html#REVIEWS"

resp = requests.get(URL, headers=HEADER, timeout=30)
bs = BeautifulSoup(resp.content, features="html.parser")


tag = bs.find('script', text=re.compile('window.__WEB_CONTEXT__'))
if tag is None:
    print("Error parse input file")
    exit(1)

data = tag.text
data = data.replace("window.__WEB_CONTEXT__=", "")
data = data.replace('{pageManifest:', '{"pageManifest":')
data = re.sub(r";\(.*$", "", data)


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


page_manifest = json.loads(data)
page_reviews = get_reviews_from_page_manifest(page_manifest)
output_list = list()
for review in page_reviews:
    output_dict = dict()
    output_dict["index"] = review.get("id")
    output_dict["published"] = review.get("publishedDate")
    output_dict["rating"] = review.get("rating")
    output_dict["title"] = review.get("title")
    output_dict["text"] = review.get("text")

    try:
        output_dict["author"] = review["userProfile"]["displayName"]
    except KeyError:
        output_dict["author"] = None

    try:
        output_dict["avatar"] = review["userProfile"]["avatar"]["photoSizes"][1]["url"]
    except KeyError:
        output_dict["avatar"] = None

    pprint(output_dict)
    output_list.append(output_dict)

print("Ok")
