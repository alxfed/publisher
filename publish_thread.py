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
from util.threadreport import create_thread_report
from util.githublog import creupdate_repo, creupdate_file


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


if __name__ == "__main__":
    # Instantiate AI
    ai = OpenAI()

    # Get thread
    number_of_messages = 100
    thread_messages = ai.beta.threads.messages.list(thread_id=agenda['thread_id'], limit=number_of_messages)
    message_data = thread_messages.data
    more = thread_messages.model_extra['has_more']

    report = create_thread_report(message_data)
    organization = config['organization']
    repository_object = creupdate_repo(repository_name=config['repository'],
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