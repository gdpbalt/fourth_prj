# -*- coding: utf-8 -*-
import requests

file_name = 'sitemap-images.txt'


def read_input_file(input_file: str) -> list:
    url_list = list()
    with open(input_file, mode='r', encoding='utf-8') as f:
        lines: list = f.readlines()

    for line in lines:
        if line:
            record = line.split('|')
            url_list.append(record[0])
    return url_list


def check_url_exist(url_in: str) -> bool:
    r = requests.get(url_in)
    if r.status_code == requests.codes.ok:
        return True
    return False


if __name__ == '__main__':
    urls = read_input_file(file_name)
    for url in urls:
        if not check_url_exist(url):
            print('Url {} not correct'.format(url))
