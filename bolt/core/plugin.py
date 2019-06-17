"""
    Description:
        Superclass for which all plugins are derived
        Provides some simple abstractions to make writing plugins easy

    Contributors:
        - Patrick Hennessy
"""
from bolt.utils.decorators import add_method_tag
from bolt.core.command import Command, RegexCommand, ParseCommand
from bolt.core.scheduler import Interval, Cron
from bolt.core.webhook import Webhook
from bolt.core.event import Subscription

from gevent import queue, GreenletExit

import logging
import inspect
import ujson as json


class Plugin(object):
    def __init__(self, bot):
        name = self.__class__.__name__

        self.bot = bot
        self.name = type(self).__name__
        self.logger = logging.getLogger(f"plugins.{name}")

        self.config = self.bot.config.plugins.get(name, {})
        self.database = bot.database_client[f"plugins-{name}"]

        self.pre_command_hooks = []
        self.commands = []
        self.webhooks = []
        self.intervals = []
        self.crons = []
        self.subscriptions = []
        self.greenlets = []
        self.greenlet_queue = queue.Queue()

        self.enabled = False

    def activate(self):
        pass

    def deactivate(self):
        pass

    def spawn_greenlet(self, callback, *args, **kwargs):
        def greenlet():
            try:
                callback(*args, **kwargs)
            except GreenletExit:
                self.logger.debug("Recieved kill signal from main thread. Exiting")
        greenlet.__name__ = callback.__name__
        self.greenlet_queue.put(greenlet)

    def load_config(self, file_path):
        raise NotImplementedError

    def load(self):
        self.logger.info(f"Loading plugin {self.name}...")

        self.activate()

        for name, callback in inspect.getmembers(self, inspect.ismethod):
            tags = getattr(callback, 'tags', [])

            for tag in tags:
                name = tag['name']
                properties = tag['properties']

                if properties.get('trigger', '') is None:
                    properties['trigger'] = self.bot.config.trigger

                if name == "pre_command":
                    self.pre_command_hooks.append(callback)

                elif name == "command":
                    command = Command(
                        properties['pattern'],
                        callback,
                        trigger=properties['trigger']
                    )
                    self.commands.append(command)

                elif name == "regex_command":
                    command = RegexCommand(
                        properties['pattern'],
                        callback,
                        trigger=properties['trigger']
                    )
                    self.commands.append(command)

                elif name == "parse_command":
                    command = ParseCommand(
                        properties['pattern'],
                        callback,
                        trigger=properties['trigger']
                    )
                    self.commands.append(command)

                elif name == "webhook":
                    webhook = Webhook(
                        properties['route'],
                        callback,
                        properties['methods']

                    )
                    self.webhooks.append(webhook)

                elif name == "interval":
                    interval = Interval(
                        properties['seconds'],
                        callback
                    )
                    self.intervals.append(interval)

                elif name == "cron":
                    cron = Cron(
                        properties['expression'],
                        callback
                    )
                    self.crons.append(cron)

                elif name == "subscriber":
                    subscription = Subscription(
                        properties['event'],
                        callback
                    )
                    self.subscriptions.append(subscription)

        self.enabled = True

    def unload(self):
        self.logger.info(f"Unloading plugin {self.name}...")
        self.deactivate()

        gevent.killall(self.greenlets)
        self.pre_command_hooks = []
        self.commands = []
        self.webhooks = []
        self.intervals = []
        self.subscribers = []

        self.enabled = False

    def enable(self):
        self.logger.info(f"Enabling plugin {self.name}...")
        self.enabled = True

    def disable(self):
        self.logger.info(f"Disabling plugin {self.name}...")
        self.enabled = False

    def say(self, channel_id, message="", embed=None, mentions=None):
        embed = {} if embed is None else embed
        mentions = [] if mentions is None else mentions

        self.logger.debug("Sending message to channel " + channel_id)

        for user in mentions:
            message = f"<@{user}> {message}"

        message_data = {
            "content": "{}".format(message),
            "embed": embed
        }

        try:
            return self.bot.api.create_message(channel_id, json.dumps(message_data))
        except Exception as e:
            self.logger.warning(f'Send message to channel "{channel_id}" failed: {e}')

    def whisper(self, user_id, message="", embed=None, mentions=None):
        embed = {} if embed is None else embed
        mentions = [] if mentions is None else mentions

        channel = self.bot.api.create_dm(user_id)
        channel_id = channel['id']

        self.say(channel_id, message=message, embed=embed, mentions=mentions)

    def upload(self, channel_id, file):
        self.logger.debug('Uploading file to channel ' + channel_id)

        endpoint = self.base_url + f"channels/{channel_id}/messages"
        files = {'file': open(file, 'rb')}

        try:
            self.bot.api.create_message(endpoint, files=files, headers=self.auth_headers)
        except Exception as e:
            self.logger.warning(f'Upload of {file} to channel {channel_id} failed: {e}')

    def __repr__(self):
        return f"Plugin({self.name})"


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


def command(pattern, trigger=None):
    return add_method_tag({
        'name': 'command',
        'properties': {
            'pattern': pattern,
            'trigger': trigger
        }
    })


def regex_command(pattern, trigger=None):
    return add_method_tag({
        'name': 'regex_command',
        'properties': {
            'pattern': pattern,
            'trigger': trigger
        }
    })


def parse_command(pattern, trigger=None):
    return add_method_tag({
        'name': 'parse_command',
        'properties': {
            'pattern': pattern,
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


def cron(expression):
    return add_method_tag({
        'name': 'cron',
        'properties': {
            'expression': expression
        }
    })


def webhook(route, methods=None):
    methods = ["GET", "POST"] if methods is None else methods

    return add_method_tag({
        'name': 'webhook',
        'properties': {
            'route': route,
            'methods': methods
        }
    })
