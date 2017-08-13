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

import logging
import sys
import os
import logging
import inspect
import importlib

class Plugin(object):
    def __init__(self, bot, name):
        self.bot = bot
        self.name = name

        self.logger = logging.getLogger(f"plugins.{self.name}")

        self.commands = []
        self.webhooks = []
        self.intervals = []
        self.subscribers = []

    def activate(self):
        pass

    def deactivate(self):
        pass

    def load(self):
        pass

    def unload(self):
        pass
    #
    # def say(self, channel_id, message="", embed={}, mentions=[]):
    #     self.logger.debug("Sending message to channel " + channel_id)
    #
    #     for user in mentions:
    #         message = "<@{}> ".format(user) + message
    #
    #     message_data = {
    #         "content": "{}".format(message),
    #         "embed": embed,
    #         "mentions": mentions
    #     }
    #
    #     try:
    #         self.api.create_message(channel_id, json.dumps(message_data))
    #     except Exception as e:
    #         self.logger.warning('Send message to channel \'{}\' failed: {}'.format(channel_id, e))
    #
    # def whisper(self, user_id, message="", embed={}, mentions=[]):
    #     channel = self.api.create_dm(user_id)
    #     channel_id = channel['id']
    #
    #     self.say(channel_id, message=message, embed=embed, mentions=mentions)
    #
    # def upload(self, channel, file):
    #     self.logger.debug('Uploading file to channel ' + channel)
    #
    #     endpoint = self.base_url + "channels/{}/messages".format(channel)
    #     files = {'file': open(file, 'rb')}
    #
    #     try:
    #         self.api.create_message(endpoint, files=files, headers=self.auth_headers)
    #     except Exception as e:
    #         self.logger.warning('Upload of {} to channel {} failed'.format(file, channel))
    #


    @classmethod
    def command(pattern, access=0, trigger=""):
        return add_method_tag({
            'name': 'command',
            'properties': {
                'access': access,
                'trigger': trigger
            }
        })

    @classmethod
    def subscribe(event):
        return add_method_tag({
            'name': 'subscriber',
            'properties': {
                'event': event,
            }
        })

    @classmethod
    def interval(seconds):
        return add_method_tag({
            'name': 'interval',
            'properties': {
                'seconds': seconds
            }
        })

    @classmethod
    def webhook(route, methods=["GET","POST"]):
        return add_method_tag({
            'name': 'webhook',
            'properties': {
                'route': route,
                'methods': methods
            }
        })


class PluginManager():
    def __init__(self, core):
        self.core = core
        self.plugins = {}
        self.logger = logging.getLogger(__name__)

    def list(self):
        return self.plugins

    def status(self, name):
        return self.plugins[name]["status"]

    def load(self, plugin_module):
        # Find plugin subclass and initialize it
        plugin = None

        for name, clazz in inspect.getmembers(plugin_module, inspect.isclass):
            if name == "Plugin":
                continue

            if issubclass(clazz, Plugin):
                plugin = clazz(self.core, name)
                break

        if not plugin:
            self.logger.error("Could not find plugin subclass in module: " + plugin_module)
            return

        # Call activate() if it exists
        if hasattr(plugin, "activate"):
            plugin.activate()

        # Register plugin commands and events
        for name, callback in inspect.getmembers(plugin, inspect.ismethod):
            if hasattr(callback, "is_command"):
                self.core.commands.register(
                    getattr(callback, "pattern"),
                    callback,
                    trigger=getattr(callback, "trigger"),
                    access=getattr(callback, "access"),
                    silent=getattr(callback, "silent")
                )

            if hasattr(callback, "is_subscriber"):
                self.core.events.subscribe(getattr(callback, "event"), callback)

        # Push plugin to our hashtable
        self.plugins[plugin.name] = {"instance":plugin, "module": plugin_module, "status": "Enabled"}
        self.logger.info("Loaded plugin \"" + plugin.name + "\"")

    def unload(self, plugin_name):
        # Check if we are managing that plugin
        if(plugin_name not in self.plugins):
            self.logger.warning("Unable to unload plugin " + plugin_name + ", plugin not loaded")
            return

        # Get plugin object from our hashtable
        plugin = self.plugins[plugin_name]["instance"]
        clazz = plugin.__class__.__name__

        if hasattr(plugin, "deactivate"):
            plugin.deactivate()

        # Unregister plugin commands and events
        for name, callback in inspect.getmembers(plugin, inspect.ismethod):
            if( hasattr(callback, "is_command") ):
                commandName = clazz + "." + callback.__name__
                self.core.commands.unregister(commandName)

            if( hasattr(callback, "is_subscriber") ):
                self.core.events.unsubscribe(getattr(callback, "event"), callback)

            if( hasattr(callback, "is_publisher") ):
                self.core.events.unregister(getattr(callback, "event"))

        # Remove from our hashtable
        self.plugins[plugin_name] = {"instance":None, "module":None, "status": "Disabled"}
        self.logger.info("Unloaded plugin \"" + plugin_name + "\"")

    def reload(self, name):
        plugin = self.plugins[name]

        if not plugin:
            return

        elif(plugin['status'] == 'Disabled'):
            self.load(name)
        else:
            self.unload(name)
            self.load(name)
