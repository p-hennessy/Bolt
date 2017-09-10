"""
    Description:
        Superclass for which all plugins are derived
        Provides some simple abstractions to make writing plugins easy

    Contributors:
        - Patrick Hennessy
"""
from arcbot.utils.decorators import add_method_tag
from arcbot.core.command import Command

import logging
import inspect
import importlib
import ujson as json

class Plugin(object):
    def __init__(self, bot):
        self.bot = bot
        self.name = __name__
        self.logger = logging.getLogger(f"plugins.{self.__class__.__name__}")

        self.pre_command_hooks = []
        self.commands = []
        self.webhooks = []
        self.intervals = []
        self.subscribers = []

        self.database = bot.database_client[f"plugins-{self.__class__.__name__}"]

        self.load()
        self.enabled = True

    def activate(self):
        pass

    def deactivate(self):
        pass

    def load(self):
        for name, callback in inspect.getmembers(self, inspect.ismethod):
            tags = getattr(callback, 'tags', [])

            for tag in tags:
                name = tag['name']
                properties = tag['properties']

                if name == "pre_command":
                    self.pre_command_hooks.append(callback)

                elif name == "command":
                    command = Command(
                        properties['pattern'],
                        callback,
                        trigger=properties['trigger'],
                        access=properties['access']
                    )

                    self.commands.append(command)

                elif name == "webhook":
                    self.bot.webhooks.add_route(
                        properties['route'],
                        callback,
                        properties['methods']
                    )

                elif name == "interval":
                    self.bot.scheduler.run_interval(
                        callback,
                        properties['seconds']
                    )

                elif name == "subscriber":
                    self.bot.events.subscribe(properties['event'], callback)


    def say(self, channel_id, message="", embed={}, mentions=[]):
        self.logger.debug("Sending message to channel " + channel_id)

        for user in mentions:
            message = f"<@{user}> {message}"

        message_data = {
            "content": "{}".format(message),
            "embed": embed
        }

        try:
            self.bot.api.create_message(channel_id, json.dumps(message_data))
        except Exception as e:
            self.logger.warning(f'Send message to channel "{channel_id}" failed: {e}')

    def whisper(self, user_id, message="", embed={}, mentions=[]):
        channel = self.bot.api.create_dm(user_id)
        channel_id = channel['id']

        self.say(channel_id, message=message, embed=embed, mentions=mentions)

    def upload(self, channel_id, file):
        self.logger.debug('Uploading file to channel ' + channel)

        endpoint = self.base_url + f"channels/{channel_id}/messages"
        files = {'file': open(file, 'rb')}

        try:
            self.bot.api.create_message(endpoint, files=files, headers=self.auth_headers)
        except Exception as e:
            self.logger.warning(f'Upload of {file} to channel {channel} failed: {e}')


def pre_command_hook():
    return add_method_tag({
        'name': 'pre_command',
        'properties': {}
    })

def help(text, usage="Not Documented"):
    return add_method_tag({
        'name': 'help',
        'properties': {
            'text': text,
            'usage': usage
        }
    })

def command(pattern, access=0, trigger="arcbot "):
    if trigger is None:
        trigger = ""

    return add_method_tag({
        'name': 'command',
        'properties': {
            'pattern': pattern,
            'access': access,
            'trigger': trigger
        }
    })

def subscriber(event):
    return add_method_tag({
        'name': 'subscriber',
        'properties': {
            'event': event,
        }
    })

def interval(seconds):
    return add_method_tag({
        'name': 'interval',
        'properties': {
            'seconds': seconds
        }
    })

def webhook(route, methods=["GET","POST"]):
    return add_method_tag({
        'name': 'webhook',
        'properties': {
            'route': route,
            'methods': methods
        }
    })
