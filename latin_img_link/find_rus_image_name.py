# -*- coding: utf-8 -*-
import os
import re
from typing import Optional

from bs4 import BeautifulSoup

xml_file_name = 'sitemap-images.xml'
out_file_name = 'sitemap-images.txt'
dictionary = {
    'ый': 'iy',
    'а': 'a',
    'б': 'b',
    'в': 'v',
    'г': 'g',
    'д': 'd',
    'e': 'e',
    'ё': 'e',
    'ж': 'zh',
    'з': 'z',
    'и': 'i',
    'й': 'y',
    'к': 'k',
    'л': 'l',
    'м': 'm',
    'н': 'n',
    'o': 'o',
    'п': 'p',
    'р': 'r',
    'с': 's',
    'т': 't',
    'у': 'u',
    'ф': 'f',
    'х': 'h',
    'ц': 'ts',
    'ч': 'ch',
    'ш': 'sh',
    'щ': 'shch',
    'ъ': '',  # пропускается
    'ы': 'y',
    'ь': '',  # пропускается
    'э': 'e',
    'ю': 'yu',
    'я': 'ya',

    'ґ': 'g',
    'є': 'ie',
    'і': 'i',
    'ї': 'i',
}


def read_xml_file(filename: str) -> Optional[str]:
    with open(xml_file_name, encoding='utf-8') as f:
        xml_txt = f.read()
    if len(xml_txt) > 0:
        return xml_txt


def parse_xml(xml: str) -> list:
    soup = BeautifulSoup(xml, 'xml')
    records = soup.find_all("image:loc")
    return [record.text for record in records]


def filename_lower(files_input: list) -> list:
    files_output = list()
    for f in files_input:
        dirname, filename, ext = get_part_of_file(f)
        files_output.append('{}/{}{}'.format(dirname, filename.lower(), ext))
    return files_output


def check_rus_letters(input_text: str) -> bool:
    if re.search(r'[а-яА-Я]', input_text):
        return True
    return False


def get_part_of_file(filename_input: str) -> list[3]:
    dirname = os.path.dirname(filename_input)
    filename = os.path.basename(filename_input)
    filename, ext = os.path.splitext(filename)
    return [dirname, filename, ext]


def find_rus_name(files_input: list) -> list:
    files_output = list()
    for filename in files_input:
        if check_rus_letters(get_part_of_file(filename)[1]):
            files_output.append(filename)
    return files_output


def translate(input_str: str) -> str:
    _input = input_str.lower()
    for key in dictionary:
        _input = _input.replace(key, dictionary[key])
    return _input


def save_result2file(files_input: list, outpu_filename: str) -> None:
    with open(outpu_filename, mode="w", encoding='utf-8') as f:
        for f1, f2 in files_input:
            f.write('{}|{}\n'.format(f1, f2))


if __name__ == '__main__':
    text = read_xml_file(xml_file_name)
    files = parse_xml(text)

    map_files_list = list()  # [0] - оригиналное имя файла, [1] - новое имя файла
    for file in files:
        file_dir, file_name, file_ext = get_part_of_file(file)
        new_file_name = translate(file_name.lower())
        new = '{}/{}{}'.format(file_dir, new_file_name, file_ext)
        if file.lower() == new:
            continue
        map_files_list.append([file, new])

    save_result2file(map_files_list, out_file_name)
