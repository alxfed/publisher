
# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import json
from openai import OpenAI, OpenAIError
from openai.resources.beta.assistants.assistants import Assistant
from openai.resources.beta.threads.threads import Thread
from openai.resources.beta.threads.runs.runs import Run
from openai.types.beta.threads import ThreadMessage
from util.githublog import creupdate_repo, creupdate_file


def create_thread_report(message_data):
    report = ''
    for message in reversed(message_data):  # reversed for chronological order of messages in the thread:
        message_text = ''
        role = message.role
        if role == 'assistant':
            message_text += f'\n> <b>{role}: </b>'
        elif role == 'user':
            message_text += f'\n <b>{role}: </b>'
        content = message.content
        for part in content:
            if part.type == 'text':
                message_text += f"{part.text.value}\n"  # part.text.value
            else:
                message_text += f" {part.type} \n"
        report += message_text
    return report


if __name__ == "__main__":
    # Load
    with open('./agenda.json', 'r') as file:
        agenda = json.load(file)

    # Instantiate AI
    ai = OpenAI()

    # Get thread
    number_of_messages = 100
    thread_messages = ai.beta.threads.messages.list(thread_id=agenda['thread_id'], limit=number_of_messages)
    message_data = thread_messages.data
    more = thread_messages.model_extra['has_more']

    report = create_thread_report(message_data)

    with open('./util/config.json', 'r') as file:
        configuration = json.load(file)

    organization = configuration['organization']
    repository_object = creupdate_repo(repository_name=configuration['repository'],
                                       description='Dialogue with an AI',
                                       private=False)
    try:
        result = creupdate_file(repository=repository_object,
                                file_path='./another_thread_report.md',
                                file_content=report,
                                branch='main')
    except Exception as e:
        print('failed ', e)

    print('ok')