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

from core.ConfigParser import *
from core.MessageParser import MessageParser
from core.Command import Command
from core.Command import CommandManager
from core.Event import EventManager
from core.User import UserManager

from connectors.slack import SlackConnection

import threading
import imp

class Bot():

    def __init__(self):
        self.botConfig = getConfig("conf/bot.conf")

        self.plugins = []
        self.event = EventManager()
        self.command = CommandManager()

        self.connection = SlackConnection(**self.botConfig["connectorOptions"])

        # Initialize core events
        self.event.register("connection.login")
        self.event.register("connection.logout")
        self.event.register("send.message")
        self.event.register("plugin.exception")

        self.login()

    def login(self):
        self.connection.connect()

    def loadPlugins(self):
        for pluginName in self.botConfig["plugins"]:
            plugin = imp.load_source(pluginName, 'plugins/' + pluginName + ".py")

            if(plugin):
                pluginThread = plugin.init(self)
                self.plugins.append(pluginThread)
