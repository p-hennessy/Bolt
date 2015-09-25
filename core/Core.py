"""
    Class Name : Core

    Description:
        Provides an extensible engine for plugins to interact with
        Features:
            - Publish / Subscribe Event System
            - Plugin manager
            - Configuration manager
            - Slack message parser
            - User, Channel and Group Date manager

    Contributors:
        - Patrick Hennessy

    License:
        PhilBot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Command import CommandManager
from core.Event import EventManager
from core.MessageConsumer import MessageConsumer
from core.Plugin import PluginManager

from connectors.discord import DiscordConnection

import threading
import imp
import json
import logging

log = logging.getLogger(__name__)

class Bot():

    def __init__(self):
        log.info("Loading configuration")
        self.config = self.loadConfig("conf/bot.conf")

        self.plugins = PluginManager(self)
        self.event = EventManager()
        self.command = CommandManager(self)

        self.connection = DiscordConnection(**self.config["connectorOptions"])

        self.messageConsumerThread = MessageConsumer(self)
        self.messageConsumerThread.daemon = True

        # Initialize core events
        self.event.register("connection.login")
        self.event.register("connection.logout")

        self.plugins.load("Chat")
        #self.login()

    def login(self):
        # Connect to the websocket
        self.connection.connect()

        self.servers = self.connection.getServers()
        self.users = self.connection.getUsers()

        # Notify login event
        self.event.notify("connection.login")

        # Start message consumer thread
        self.messageConsumerThread.start()

        #self.connection.say("96451923229556736", "**CL4M-B0T** login successful.")

    def logout(self):
        # Send stop to message consumer, wait for it to finish it's run.
        self.messageConsumerThread.stop()
        self.messageConsumerThread.join()

        # Send stop to all plugins

        # Disconnect from the websocket
        self.connection.disconnect()

        # Notify logout event
        self.event.notify("connection.logout")

    def loadConfig(self, fileName):
        configData = None

        with open(fileName) as file:
            configData = json.load(file)

        return configData

    def loadConnector(self):
        pass

    def loadPlugins(self):
        for plugin in self.config["plugins"]:
            self.loadPlugin(plugin)

    def loadPlugin(self, name):
        plugin = imp.load_source(name, 'plugins/' + name + ".py")

        if(plugin):
            pluginThread = plugin.init(self)
            self.plugins.append(pluginThread)

    def stopPlugin(self):
        pass
