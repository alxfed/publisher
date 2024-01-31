# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from typing import List, Dict
from dataclasses import dataclass, field, asdict
from time import sleep
import json
import jsonlines
from openai import OpenAI, OpenAIError
from openai.resources.beta.assistants.assistants import Assistant
from openai.resources.beta.threads.threads import Thread
from openai.resources.beta.threads.runs.runs import Run
from openai.types.beta.threads import ThreadMessage


@dataclass
class Utterance:
    author:       str = field(default="")
    utterance:    str = field(default="This is a content of a message.")

    def to_dict(self):
        return asdict(self)


class Conversation():
    """Represents a conversation."""
    ai:                 OpenAI
    assistant:          Assistant
    thread:             Thread
    message:            ThreadMessage
    run:                Run
    record:             List[Utterance] = []
    assistant_config:   Dict = field(default_factory=dict)
    agenda:             Dict = field(default_factory=dict)

    topic:          str = ""
    user_name:      str = ""
    assistant_name: str = ""
    assistant_id:   str = ""
    thread_id:      str = ""
    run_id:         str = ""
    run_status:     str = ''
    run_step:       str = ''
    record_file:    str = './record.jsonl'

    def __init__(self, ai: OpenAI, **kwargs):
        self.ai = ai
        self.agenda = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
        super(Conversation, self).__init__()

    def enter(self):
        if self.assistant_id == '':
            description = self._load_assistant_description()
            try:
                self.assistant = self.ai.beta.assistants.create(**description)
                self.agenda['assistant_id'] = self.assistant.id
                self._save_agenda()
            except Exception as e:
                print("Unable to create assistant. ")
                print(f"Exception: {e}")
                return
        # Create an initial message setting the topic of the conversation
        topic_setter = {
            "role": "user",
            "content": f"{self.user_name}: The topic of this conversation will be: '{self.topic}'"
        }
        if self.thread_id == '':
            try:
                self.thread = self.ai.beta.threads.create(messages=[topic_setter])
                self.agenda['thread_id'] = self.thread.id
                self._save_agenda()
            except Exception as e:
                print("Unable to create thread. ")
                print(f"Exception: {e}")
                return

    def add_utterance(self, utterance: Utterance):
        message_to_add = {
            "role": "user",
            "content": f"{utterance.author}: {utterance.utterance}"
        }
        try:
            self.message = self.ai.beta.threads.messages.create(thread_id=self.thread.id, **message_to_add)
        except Exception as e:
            print("Unable to add utterance. ")
            print(f"Exception: {e}")
            return
        self._save_utterance(utterance)
        self.record.append(utterance)

    def get_response(self):
        try:
            self.run = self.ai.beta.threads.runs.create(thread_id=self.thread.id, assistant_id=self.assistant.id)
            count = 0
        except Exception as e:
            print("Unable to create a run. ")
            print(f"Exception: {e}")
            raise(RuntimeError("Unable to create a run. "))
        while True:
            count += 1
            if count > 1:
                sleep(2)
            # self.run_step = self.run.step
            self.run = self.ai.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=self.run.id)
            # queued, in_progress, requires_action, cancelling, cancelled, failed, completed, or expired
            self.run_status = self.run.status
            if self.run_status == 'queued':
                pass
            elif self.run_status == 'in_progress':
                pass
            elif self.run_status == 'requires_action':
                # Tools need to be invoked to complete the run
                self._use_tools()
            elif self.run_status == 'cancelling':
                pass
            elif self.run_status == 'cancelled':
                raise RuntimeError("Run cancelled.")
            elif self.run_status == 'failed':
                raise RuntimeError("Run failed.")
            elif self.run_status == 'completed':
                break
            elif self.run_status == 'expired':
                raise RuntimeError("Run expired.")
            else:
                raise RuntimeError("Run expired.")
            # if count > 200:
            #     raise RuntimeError("Run is taking too long. ")

        thread_messages = self.ai.beta.threads.messages.list(thread_id=self.thread.id)
        message_data = thread_messages.data
        new_message = message_data[0]
        if new_message.role == 'assistant' and new_message.assistant_id == self.assistant.id:
            content = new_message.content
            first_element = content[0]
            if first_element.type == 'text':
                tex = first_element.text.value
                utterance = Utterance(utterance=tex, author=self.assistant_name)
                self._save_utterance(utterance)
                self.record.append(utterance)
                return tex
            elif first_element['type'] == 'image':
                pass
            else:
                print('Not a text response.')

    def _use_tools(self):
        # self.run is in a 'requires_action' state.
        """ "required_action": {
        "type": "submit_tool_outputs",
        "submit_tool_outputs": {
          "tool_calls": [
            {
              "id": "call_abc123",
              "type": "function",
              "function": {
                "name": "getCurrentWeather",
                "arguments": "{\"location\":\"San Francisco\"}"
              }
            },
            {
              "id": "call_abc456",
              "type": "function",
              "function": {
                "name": "getNickname",
                "arguments": "{\"location\":\"Los Angeles\"}"
              }
            }
          ]
        }
        """
        pass

    def _save_utterance(self, utterance: Utterance):
        with jsonlines.open('./record.jsonl', 'a') as writer:
            writer.write(utterance.to_dict())

    def load_record(self):
        with jsonlines.open('./record.jsonl', 'r') as reader:
            self.record = [Utterance(**line) for line in reader.iter()]

    def _load_agenda(self):
        with open('./agenda.json', 'r') as file:
            self.agenda = json.load(file)

    def _load_assistant_description(self):
        with open('./hidden/assistant.json', 'r') as file:
            return json.load(file)

    def _save_agenda(self):
        with open('./agenda.json', 'w') as file:
            json.dump(self.agenda, file)

    def next_statement(self):
        return self.record.pop(0)

    def publish(self):
        pass

    def stop(self):
        self._save_agenda()

    def end(self):
        self._delete_scaffolds()
        # TODO: delete the ids here
        self._save_agenda()


if __name__ == '__main__':
    print('main')
