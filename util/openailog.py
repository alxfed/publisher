# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import json
import jsonlines
from time import sleep
from  recorder import save_all_records
from util.githublog import creupdate_repo, creupdate_file
# import septem_circumstantiae as resources
# import importlib.resources as impres
#
#
# # https://importlib-resources.readthedocs.io/en/latest/using.html
# with impres.files(resources).joinpath('resources/who.text').open('r', encoding='utf-8') as file:
#     text = file.readline()
#     all_text = file.read()


def ingest_json(file_path):
    with open(file_path, 'r') as file:
        conversations = json.load(file)
    return conversations


def extract_content(message):
    text = ''.join(message['content']['parts'])
    text = text.replace('\\[','$$')
    text = text.replace('\\]','$$')
    text = text.replace('\\(','$')
    text = text.replace('\\)','$')
    text = text.replace('\n\n','<br>')
    text = text.replace('\n   -','<br>-')
    return text


def process_system_message(message):
    processed_message = None
    text = ''.join(message['content']['parts'])
    if text != '':
        processed_message = text
    return processed_message


def process_user_message(message):
    return extract_content(message)


def process_assistant_message(message):
    return extract_content(message)


def process_conversation(conversation, agenda: dict):
    messages = conversation['mapping']
    record = []
    for key, value in messages.items():
        # child = value['children'][0]  # The last message doesn't have children
        # message_id = value['id']
        if value['message'] is not None:
            present_message = value['message']
            author_role = present_message['author']['role']
            author_name = present_message['author']['name']
            if author_role == 'user':
                result = process_user_message(present_message)
                author_name = agenda['user_name'] if author_name is None else author_name
                record.append({"author": author_name, "utterance": result})
            elif author_role == 'system':
                result = process_system_message(present_message)
                if result is not None:
                    author_name = agenda['system_name'] if author_name is None else author_name
                    record.append({"author": author_name, "utterance": result})
                else:
                    pass
            elif author_role == 'assistant':
                result = process_assistant_message(present_message)
                author_name = agenda['assistant_name'] if author_name is None else author_name
                record.append({"author": author_name, "utterance": result})
            else:
                pass
        else:
            # message is None
            pass
    return record


if __name__ == '__main__':
    print('you opened a utility file as main')
