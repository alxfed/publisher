# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import jsonlines


def ingest_records(file_path):
    with jsonlines.open('./record.jsonl', 'r') as reader:
        records = [line for line in reader.iter()]
    return records


def save_one_record(record):
    with jsonlines.open('./record.jsonl', 'a') as writer:
        writer.write(record)


def save_all_records(records_list):
    with jsonlines.open('./record.jsonl', 'a') as writer:
        for record in records_list:
            writer.write(record)


if __name__ == '__main__':
    records = [
        {"author": "Alex", "utterance": 'This is a content of a message.'},
        {'author': 'machina', 'utterance': 'This is a content of a message.'}
    ]
    save_all_records(records)
    records = ingest_records('./record.jsonl')
    save_one_record(records[0])
    print('ok')