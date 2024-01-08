# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import json
# import jsonlines
import os
from conversation import Conversation, Utterance
from openai import OpenAI
from dotenv import load_dotenv
from typing_extensions import Literal
load_dotenv()
ai = OpenAI()


def load_agenda():
    with open('./agenda.json', 'r') as file:
        agenda = json.load(file)
    return agenda


def clean_up():
    """ Cleans up all data.
    """
    agenda = load_agenda()
    if agenda['thread_id'] != '':
        try:
            result =ai.beta.threads.delete(agenda['thread_id'])
            agenda['thread_id'] = ''
        except Exception as e:
            print(f"Thread already deleted. {e}")
    if agenda['assistant_id'] != '':
        try:
            result= ai.beta.assistants.delete(agenda['assistant_id'])
            agenda['assistant_id'] = ''
        except Exception as e:
            agenda['assistant_id'] = ''
            print(f"Assistant already deleted. {e}")
    with open('./agenda.json', 'w') as file:
        json.dump(agenda, file)
    return agenda


def delete_record(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"{file_path} has been deleted")


def main(agenda: dict):
    """ Initiate a new conversation.
    """
    # Instantiate a conversation.
    conv = Conversation(ai=ai, **agenda)

    # Begin
    conv.enter()
    go_on = True

    while go_on:
        user_said = input(f'{conv.user_name}: ')
        if user_said != ('stop' or 'end'):
            new_utterance = {"author": conv.user_name,"utterance": user_said}
            try:
                utt = Utterance(**new_utterance)
                conv.add_utterance(utt)
                response = conv.get_response()
                print(f'{conv.assistant_name}: {response}')
            except Exception as e:
                print(f"Error: {e}")
                break
        elif user_said == 'stop':
            conv.stop()
            go_on = False
            print("Conversation stopped.")
        elif user_said == 'end':
            conv.end()
            go_on = False
            print("End of conversation.")
        else:
            user_said = input('Would you like to publish this conversation? [y/n] ')
            if user_said == 'y':
                conv.publish()
            go_on = False
            print("End of conversation")


if __name__ == "__main__":
    user_said = input(f'Do you want to start a new conversation? [y/n/continue/restart/clean] ')

    if user_said == 'y':
        agenda = clean_up()
        delete_record(file_path=agenda['record_file'])
        main(agenda=agenda)
    elif user_said == 'n':
        print("Not going to do anything. Goodbye!")
    elif user_said == 'continue':
        main(agenda=load_agenda())
    elif user_said == 'restart':
        main(agenda=load_agenda())
    elif user_said == 'clean':
        agenda = clean_up()
        delete_record(file_path=agenda['record_file'])
        print("All have been cleaned up.")
    exit()
