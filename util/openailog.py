# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import json
from util.recorder import save_all_records


def ingest_json(file_path):
    with open(file_path, 'r') as file:
        conversations = json.load(file)
    return conversations


def extract_content(message):
    text = ''.join(message['content']['parts'])
    return text


def process_system_message(message):
    processed_message = message
    return processed_message


def process_user_message(message):
    return extract_content(message)


def process_assistant_message(message):
    return extract_content(message)


def process_conversation(conversation):
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
                author_name = config['user_name'] if author_name is None else author_name
                record.append({"author": author_name, "utterance": result})
            elif author_role == 'system':
                _ = process_system_message(present_message)
            elif author_role == 'assistant':
                result = process_assistant_message(present_message)
                author_name = config['assistant_name'] if author_name is None else author_name
                record.append({"author": author_name, "utterance": result})
            else:
                pass
        else:
            # message is None
            pass
    return record


def print_out(record):
    for utterance in record:
        print(utterance)


def publish():
    print('Publishing...')


if __name__ == '__main__':
    config = ingest_json('./util/config.json')
    conversations_list = ingest_json(f'{config["conversations_dir"]}conversations.json')
    for conv in conversations_list:
        list_of_utterances = process_conversation(conv)
        decision = input('What should I do with it? (p - publish, s - save record,<enter> - skip, stop):  ')
        if decision == 'stop':
            break
        elif decision == 'p':
            publish()
        elif decision == 's':
            save_all_records(list_of_utterances)

    print('That is all. Goodbye.')
