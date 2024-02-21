# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import json
import jsonlines
from time import sleep
from util.openailog import ingest_json, process_conversation
from util.recorder import save_all_records
from util.githublog import creupdate_repo, creupdate_file


# Configuration of the meaning and implementation.
agenda = {
  "topic": "Business strategy for small AI companies",
  "user_name": "Alex",
  "assistant_name": "ChatGPT",
  "other_persons": [],
  "assistant_id": "",
  "thread_id": "",
  "run_id": "",
  "record_file": "./record.jsonl"
}
config = {
  "conversations_dir": "/home/alxfed/Downloads/chatgpt/",
  "files_dir": "./files",
  "organization": "ai-dialogue-facilitator",
  "repository": "business-strategy",
  "file_path": "./README.md",
  "user_name": "Alex",
  "assistant_name": "ChatGPT",
  "system_name": "system",
  "model_name": "gpt-3.5-turbo-1106"
}


def make_md_file(agenda: dict, record_list: list):
    # Header
    md_text = f'# {agenda["topic"]}\n'

    # Body
    for record in record_list:
        if record['author'] == agenda['user_name']:
            md_text += f'\n<b>{record["author"]}:</b> {record["utterance"]}<br>'
        elif record['author'] == agenda['assistant_name']:
            md_text += f'\n><b>{record["author"]}:</b> {record["utterance"]}<br>\n'
        else:
            print('Unexpected author')
    return md_text


def publish(configuration: dict, index: int, record_list: list):
    human_says = input('Branch name? ("Enter" for "main") ')
    if human_says == '':
        branch = 'main'
    else:
        branch = human_says
    # Create the README.md file
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


def print_out(record):
    for utterance in record:
        print(utterance)


if __name__ == '__main__':
    directory = config["conversations_dir"]
    conversations_list = ingest_json(f'{directory}conversations.json')
    for index,conv in enumerate(conversations_list):
        list_of_utterances = process_conversation(conv, agenda)
        decision = input('What should I do with it? (p - publish, s - save record,<enter> - skip, stop):  ')
        if decision == 'stop':
            break
        elif decision == 'p':
            publish(configuration=config, index=index, record_list=list_of_utterances)
        elif decision == 's':
            save_all_records(list_of_utterances)

    print('That is all. Goodbye.')
