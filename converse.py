# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import json
import jsonlines
import os
from conversation import Conversation, Utterance
from util.githublog import creupdate_repo, creupdate_file
from openai import OpenAI
from dotenv import load_dotenv
from typing_extensions import Literal
load_dotenv()
ai = OpenAI()


def load_agenda():
    with open('./agenda.json', 'r') as file:
        agenda = json.load(file)
    return agenda


def make_md_file(agenda: dict):
    md_text = f'# {agenda["topic"]}\n'
    with jsonlines.open(agenda['record_file'], 'r') as reader:
        for record in reader:
            if record['author'] == agenda['user_name']:
                md_text += f'\n<b>{record["author"]}:</b> {record["utterance"]}<br>'
            elif record['author'] == agenda['assistant_name']:
                md_text += f'\n> <b>{record["author"]}:</b> {record["utterance"]}<br>\n'
            else:
                print('Unexpected author')
    return md_text


def clean_up():
    """ Cleans up all objects created.
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
    """ Deletes a record of conversation."""
    if os.path.exists(file_path):
        os.remove(file_path)
        # print(f"{file_path} has been deleted")


def main(agenda: dict):
    """ Initiate a dialogue.
    """
    # Instantiate a conversation.
    this_conversation = Conversation(ai=ai, **agenda)

    # Begin
    this_conversation.enter()
    go_on = True

    # Go on until user wants to stop
    while go_on:
        """ Next step of the conversation.
        """
        user_said = input(f'{this_conversation.user_name}: ')
        if user_said == 'stop':
            this_conversation.stop()
            go_on = False
            print("Conversation stopped.")
        elif user_said == 'end':
            this_conversation.stop()
            # TODO: delete objects
            go_on = False
            print("End of conversation.")
        else:
            new_utterance = {"author": this_conversation.user_name, "utterance": user_said}
            try:
                utt = Utterance(**new_utterance)
                this_conversation.add_utterance(utt)
                response = this_conversation.get_response()
                print(f'{this_conversation.assistant_name}: {response}')
            except Exception as e:
                print(f"Error: {e}")
                break
    # user_said = input('Would you like to publish this conversation? [y/n] ')
    # if user_said == 'y':
    #     this_conversation.publish()
    print("End of conversation")


if __name__ == "__main__":
    human_says = input(f'Do you want to start a new conversation? [y/n/continue/restart/clean/publish] ')
    if human_says == 'y':
        this_agenda = clean_up()
        delete_record(file_path=this_agenda['record_file'])
        main(agenda=this_agenda)
    elif human_says == 'n':
        print("Not going to do anything. Goodbye!")
    elif human_says == 'continue':
        main(agenda=load_agenda())
    elif human_says == 'restart':
        main(agenda=load_agenda())
    elif human_says == 'publish':
        human_says = input('Branch name? ("Enter" for "main") ')
        if human_says == '':
            branch = 'main'
        else:
            branch = human_says
        # Create the README.md file
        this_agenda = load_agenda()
        md_file = make_md_file(this_agenda)
        # Creupdate the repository
        with open('./util/config.json', 'r') as file:
            configuration = json.load(file)
        organization = configuration['organization']
        repository_object = creupdate_repo(repository_name=configuration['repository'],
                                           description='Dialogue with an AI',
                                           private=False)
        try:
            result = creupdate_file(repository=repository_object,
                                    file_path='./README.md',
                                    file_content=md_file,
                                    branch=branch)
        except Exception as e:
            print('failed ', e)
        try:
            result = creupdate_file(repository=repository_object,
                                    file_path='./agenda.json',
                                    file_content=json.dumps(this_agenda),
                                    branch=branch)
        except Exception as e:
            print('failed ', e)

    elif human_says == 'clean':
        this_agenda = clean_up()
        delete_record(file_path=this_agenda['record_file'])
        print("All have been cleaned up.")
    exit()
