import json
import re

import requests
from bs4 import BeautifulSoup

# https://stackoverflow.com/questions/56682371/scraping-a-website-with-data-hidden-under-read-more
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


def get_reviews_from_page_manifest(input_data: dict):
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
print("Ok")
