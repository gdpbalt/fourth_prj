import datetime

from control.settings import LANGS

MONTH_LIST_RUS = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
MONTH_LIST_UKR = ['січ', 'лют', 'бер', 'кві', 'тра', 'чер', 'лип', 'сер', 'вер', 'жов', 'лис', 'гру']


def date2str(mydate: datetime.date, lang=LANGS[0]):
    if lang == LANGS[1]:
        return f"{mydate.day} {MONTH_LIST_UKR[mydate.month - 1]}"
    return f"{mydate.day} {MONTH_LIST_RUS[mydate.month - 1]}"


def location_from(transport, city, lang=LANGS[0]):
    if lang == LANGS[1]:
        return "{} із {}".format(transport, city)
    return "{} из {}".format(transport, city)


def date_duration(tour_start, tour_length, lang=LANGS[0]):
    date_string = date2str(tour_start, lang=lang)
    if lang == LANGS[1]:
        return "{} на {} ночей/{} днів".format(date_string, tour_length-1, tour_length)
    return "{} на {} ночей/{} дней".format(date_string, tour_length-1, tour_length)
