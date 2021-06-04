# -*- coding: utf-8 -*-
import argparse
from time import sleep

from control.classes.api_otpusk import MethodCountries, MethodFromCities, MethodCities, MethodOperators
from control.models import OtpuskCities, OtpuskCoutries
from control.settings import API, LANGS
from control.utils.request import get_method_link_prepend, get_method_link_append


def sync_countries():
    base = get_method_link_prepend(method=API['method_countries'])
    for lang_id, lang_name in enumerate(LANGS):
        url = base + get_method_link_append(lang=lang_name)
        response = MethodCountries(link=url, lang_id=lang_id)
        response.run()
        sleep(2)


def sync_from_cities():
    base = get_method_link_prepend(method=API['method_from_cities'])
    for lang_id, lang_name in enumerate(LANGS):
        url = base + get_method_link_append(lang=lang_name)
        response = MethodFromCities(link=url, lang_id=lang_id)
        response.run()
        sleep(2)


def sync_operators():
    base = get_method_link_prepend(method=API['method_operators'])
    for lang_id, lang_name in enumerate(LANGS):
        url = base + get_method_link_append(lang=lang_name)
        response = MethodOperators(link=url, lang_id=lang_id)
        response.run()
        sleep(2)


def count_of_cities(country_id, lang_id):
    sql = OtpuskCities.query
    sql = sql.filter(OtpuskCities.lang == lang_id)
    sql = sql.filter(OtpuskCities.country == country_id)
    cities = sql.all()
    if (count_cities := len(cities)) == 0:
        return 0
    return count_cities


def sync_cities():
    base = get_method_link_prepend(method=API['method_cities'])
    lang_rus = LANGS.index('rus')
    countries = OtpuskCoutries.query.filter_by(lang=lang_rus).all()
    for country in countries:
        for lang_id, lang_name in enumerate(LANGS):
            url = "{}countryId={}&{}".format(base, country.otpusk_id, get_method_link_append(lang=lang_name))
            print(url)
            response = MethodCities(link=url, lang_id=lang_id, country=country.otpusk_id)
            response.run()
            sleep(5)


if __name__ == "__main__":
    cmd = argparse.ArgumentParser()
    cmd.add_argument('--countries', dest='countries', action='store_const', const=True,
                     help="Sync otpusk.countries with dbase")
    cmd.add_argument('--from', dest='from_cities', action='store_const', const=True,
                     help="Sync otpusk.from_cities with dbase")
    cmd.add_argument('--operators', dest='operators', action='store_const', const=True,
                     help="Sync otpusk.operators with dbase")
    cmd.add_argument('--cities', dest='cities', action='store_const', const=True,
                     help="Sync otpusk.cities with dbase")

    args = cmd.parse_args()
    if args.countries:
        sync_countries()
    elif args.from_cities:
        sync_from_cities()
    elif args.operators:
        sync_operators()
    elif args.cities:
        sync_cities()
