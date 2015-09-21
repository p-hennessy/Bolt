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

from core.Command import Command
from core.Command import CommandManager
from core.Event import EventManager
from core.User import UserManager
from core.Channel import ChannelManager
from core.MessageConsumer import MessageConsumer

from connectors.slack import SlackConnection

import threading
import imp
import json

class Bot():

    def __init__(self):
        self.config = self.loadConfig("conf/bot.conf")

        self.plugins = []
        self.event = EventManager()
        self.command = CommandManager(self)

        self.connection = SlackConnection(**self.config["connectorOptions"])

        self.user = UserManager(self)
        self.channel = ChannelManager(self)

        self.messageConsumerThread = MessageConsumer(self)
        self.messageConsumerThread.daemon = True

        # Initialize core events
        self.event.register("connection.login")
        self.event.register("connection.logout")

        self.loadPlugins()
        self.login()

    def login(self):
        # Connect to the websocket
        self.connection.connect()

        # Notify login event
        self.event.notify("connection.login")

        # Start message consumer thread
        self.messageConsumerThread.start()

        # Get our channel and user data up to date
        self.user.updateUserList()
        self.channel.updateChannelList()

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
        for pluginName in self.config["plugins"]:
            plugin = imp.load_source(pluginName, 'plugins/' + pluginName + ".py")

            if(plugin):
                pluginThread = plugin.init(self)
                self.plugins.append(pluginThread)
