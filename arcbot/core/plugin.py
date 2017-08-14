"""
    Class Name : Plugin

    Description:
        Superclass for which all plugins are derived

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""
from arcbot.utils.decorators import add_method_tag
from arcbot.core.command import Command

import logging
import sys
import os
import logging
import inspect
import importlib
import ujson as json

class Plugin(object):
    def __init__(self, bot):
        self.bot = bot
        self.name = __name__
        self.logger = logging.getLogger(f"plugins.{self.name}")

        self.commands = []
        self.webhooks = []
        self.intervals = []
        self.subscribers = []

        self.load()
        self.enabled = True

    def load(self):
        for name, callback in inspect.getmembers(self, inspect.ismethod):
            tags = getattr(callback, 'tags', [])

            for tag in tags:
                if tag['name'] == "command":
                    command = Command(
                        tag['properties']['pattern'],
                        callback,
                        trigger=tag['properties']['trigger'],
                        access=tag['properties']['access']
                    )

                    self.commands.append(command)

                elif tag['name'] == "webhook":
                    #self.bot.webhook.add_route()
                    pass

                elif tag['name'] == "interval":
                    #self.bot.scheduler.add()
                    pass

                elif tag['name'] == "subscriber":
                    pass

    def say(self, channel_id, message="", embed={}, mentions=[]):
        self.logger.debug("Sending message to channel " + channel_id)

        for user in mentions:
            message = f"<@{user}> {message}"

        message_data = {
            "content": "{}".format(message),
            "embed": embed,
            "mentions": mentions
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


    # Decorators
    @staticmethod
    def command(pattern, access=0, trigger="arcbot "):
        return add_method_tag({
            'name': 'command',
            'properties': {
                'pattern': pattern,
                'access': access,
                'trigger': trigger
            }
        })

    @staticmethod
    def subscribe(event):
        return add_method_tag({
            'name': 'subscriber',
            'properties': {
                'event': event,
            }
        })

    @staticmethod
    def interval(seconds):
        return add_method_tag({
            'name': 'interval',
            'properties': {
                'seconds': seconds
            }
        })

    @staticmethod
    def webhook(route, methods=["GET","POST"]):
        return add_method_tag({
            'name': 'webhook',
            'properties': {
                'route': route,
                'methods': methods
            }
        })
