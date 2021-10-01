import re
from typing import Optional

from bs4 import BeautifulSoup

from control import app


class TAParsePattern:
    def print_error(self, msg: str) -> None:
        app.logger.warning("{}. {}".format(self.logprefix, msg))

    def ta_parse_hotel_name_full(self, key: str, response: BeautifulSoup) -> Optional[str]:
        tag = response.find("h1", class_=["header heading masthead masthead_h1"])
        if not tag:
            self.print_error(f"{key}: not found")
            return
        return tag.text

    @staticmethod
    def ta_parse_hotel_name(key: str, text: str) -> Optional[str]:
        text = re.sub(r'Отель', '', text).strip()
        names = text.split(",")
        if not names:
            return text

        text = names[0]
        text = re.sub(r'\d.*\*', '', text).strip()

        return text

    def ta_parse_hotel_stars(self, key: str, text: str) -> Optional[float]:
        results = re.findall(r'\s(\d.*)\*', text)
        if not results:
            self.print_error(f"{key}: not found")
            return

        try:
            number = float(results[0])
        except Exception as e:
            self.print_error(f"{key}: can't convert to float ({e})")
            return

        return number

    def ta_parse_number_reviews(self, key: str, response: BeautifulSoup) -> Optional[int]:
        tag = response.find("span", class_="btQSs q Wi z Wc")
        if not tag or tag.is_empty_element:
            self.print_error(f"{key}: not found or empty")
            return

        text_orig = tag.next.text
        if not text_orig:
            self.print_error(f"{key}: not found")
            return

        text = re.sub(r'\s', '', text_orig)
        results = re.findall(r'^(\d+)', text)
        if not results:
            self.print_error(f"{key}: numbers not found in input string {text_orig}")
            return

        try:
            number = int(results[0])
        except Exception as e:
            self.print_error(f"{key}: can't convert to int ({e})")
            return

        return number

    def ta_parse_rate(self, key: str, response: BeautifulSoup) -> Optional[float]:
        tag = response.find("span", class_="bvcwU P")
        if not tag:
            self.print_error(f"{key}: not found")
            return

        value = tag.text
        value = value.replace(",", ".")

        try:
            number = float(value)
        except Exception as e:
            self.print_error(f"{key}: can't convert to float ({e})")
            return
        return number

    def ta_parse_page(self, key: str, response: BeautifulSoup) -> Optional[float]:
        tag = response.find("span", class_="pageNum current disabled")
        if not tag:
            self.print_error(f"{key}: not found")
            return

        value = tag.text
        value = value.replace(" ", "")

        try:
            number = int(value)
        except Exception as e:
            self.print_error(f"{key}: can't convert to int ({e})")
            return
        return number

    def ta_parse_post_index(self, key: str, response: BeautifulSoup) -> Optional[int]:
        tag = response.find("div", attrs={"data-reviewid": True})
        if not tag:
            self.print_error(f"{key}: not found")
            return

        try:
            number = int(tag.attrs["data-reviewid"])
        except Exception as e:
            self.print_error(f"{key}: can't convert to int ({e})")
            return
        return number

    def ta_parse_post_author(self, key: str, response: BeautifulSoup) -> Optional[str]:
        tag = response.find("a", class_="ui_header_link bPvDb")
        if not tag:
            self.print_error(f"{key}: not found")
            return
        return tag.text

    @staticmethod
    def ta_parse_post_author_geo(key: str, response: BeautifulSoup) -> Optional[str]:
        tag = response.find("span", class_="fSiLz")
        if not tag:
            return
        return tag.text

    def ta_parse_post_date(self, key: str, response: BeautifulSoup) -> Optional[str]:
        tag = response.find("div", class_="bcaHz")
        if not tag:
            self.print_error(f"{key}: not found")
            return

        text = tag.text
        search_pattern = "написал(а) отзыв"
        results = text.split(search_pattern)
        if (num := len(results)) == 0:
            self.print_error(f"{key}: can't find text '{search_pattern}'")
            return
        else:
            return "{} {}".format(search_pattern, results[num - 1].strip())

    def ta_parse_post_date_stay(self, key: str, response: BeautifulSoup) -> Optional[str]:
        tag = response.find("span", class_="euPKI _R Me S4 H3")
        if not tag:
            self.print_error(f"{key}: not found")
            return

        pattern = "Дата пребывания:"
        text = re.sub(pattern, "", tag.text).strip()

        return text

    def ta_parse_post_rate(self, key: str, response: BeautifulSoup) -> Optional[float]:
        tag = response.find("span", class_="ui_bubble_rating")
        if not tag:
            self.print_error(f"{key}: not found")
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
            self.print_error(f"{key}: can't convert to int ({e})")
            return
        return number / 10

    def ta_parse_post_title(self, key: str, response: BeautifulSoup) -> Optional[str]:
        tag = response.find("div", class_="fpMxB MC _S b S6 H5 _a")
        if not tag:
            self.print_error(f"{key}: not found")
            return
        return tag.text

    def ta_parse_post_text(self, key: str, response: BeautifulSoup) -> list:
        texts = list()

        tag = response.find("q", class_="XllAv H4 _a")
        if not tag:
            self.print_error(f"{key}: not found")
            return texts

        tags = tag.find_all("span")
        for key, tag in enumerate(tags):
            if key > 1:
                break
            texts.append(tag.text)

        return texts
