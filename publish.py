# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import json
import jsonlines
from time import sleep
from util.recorder import save_all_records
from util.githublog import creupdate_repo, creupdate_file


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
                result = process_system_message(present_message)
                if result is not None:
                    author_name = config['system_name'] if author_name is None else author_name
                    record.append({"author": author_name, "utterance": result})
                else:
                    pass
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


def make_md_file(agenda: dict, record_list: list):
    md_text = f'# {agenda["topic"]}\n'

    for record in record_list:
        if record['author'] == agenda['user_name']:
            md_text += f'\n<b>{record["author"]}:</b> {record["utterance"]}<br>'
        elif record['author'] == agenda['assistant_name']:
            md_text += f'\n> <b>{record["author"]}:</b> {record["utterance"]}<br>\n'
        else:
            print('Unexpected author')
    return md_text


def print_out(record):
    for utterance in record:
        print(utterance)


def publish(configuration: dict, record_list: list):
    human_says = input('Branch name? ("Enter" for "main") ')
    if human_says == '':
        branch = 'main'
    else:
        branch = human_says
    # Create the README.md file
    with open('./agenda.json', 'r') as file:
        agenda = json.load(file)
    md_file = make_md_file(agenda=agenda, record_list=record_list)
    # Creupdate the repository
    organization = configuration['organization']
    repository_object = creupdate_repo(repository_name=configuration['repository'],
                                       organization=organization,
                                       description='Dialogue with an AI',
                                       private=False)
    sleep(10)
    try:
        print('Publishing...')
        filepath = configuration['file_path']
        result = creupdate_file(repository=repository_object,
                                file_path=filepath,
                                file_content=md_file,
                                branch=branch)
    except Exception as e:
        print('failed ', e)
    try:
        result = creupdate_file(repository=repository_object,
                                file_path='./agenda.json',
                                file_content=json.dumps(agenda),
                                branch=branch)
    except Exception as e:
        print('failed ', e)


if __name__ == '__main__':
    config = ingest_json('./util/config.json')
    directory = config["conversations_dir"]
    conversations_list = ingest_json(f'{directory}conversations.json')
    for conv in conversations_list:
        list_of_utterances = process_conversation(conv)
        decision = input('What should I do with it? (p - publish, s - save record,<enter> - skip, stop):  ')
        if decision == 'stop':
            break
        elif decision == 'p':
            publish(configuration=config, record_list=list_of_utterances)
        elif decision == 's':
            save_all_records(list_of_utterances)

    print('That is all. Goodbye.')
