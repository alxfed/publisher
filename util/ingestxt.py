# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""


def ingest_paragraphs_of_txt(file_path):
    list_of_paragraphs = []
    with open(file_path, 'r') as file:
        for line in file:
            list_of_paragraphs.append(line)
    return list_of_paragraphs


def ingest_all_txt(file_path):
    list_of_paragraphs = []
    with open(file_path, 'r') as file:
        for line in file:
            list_of_paragraphs.append(line)
    return list_of_paragraphs


if __name__ == '__main__':
    paragraphs = ingest_paragraphs_of_txt('/home/alxfed/Documents/Adler/Hypothesis.txt')
    print('ok')