# -*- coding: utf-8 -*-
import os

file_name = 'sitemap-images.txt'
basedir = '/tmp'


def read_input_file(input_file: str) -> list:
    url_list = list()
    with open(input_file, mode='r', encoding='utf-8') as f:
        lines: list = f.readlines()

    for line in lines:
        if line:
            line = line.rstrip()
            record = line.split('|')
            url_list.append(record)
    return url_list


def get_part_of_file(filename_input: str) -> list[2]:
    dirname = os.path.dirname(filename_input).lstrip('https://antonivtours.com/')
    filename = os.path.basename(filename_input)
    return [dirname, filename]


if __name__ == '__main__':
    urls = read_input_file(file_name)
    for old, new in urls:
        old_dir, old_file = get_part_of_file(old)
        new_dir, new_file = get_part_of_file(new)

        cmd = 'mv {}/{}/{} {}/{}/{}'.format(basedir, old_dir, old_file,
                                            basedir, old_dir, new_file)
        print(cmd)
