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

from core.SlackWebSocket import *
from core.ConfigParser import *
from core.MessageParser import MessageParser
from core.Command import Command
from core.Command import CommandManager
from core.Event import EventManager
from core.User import UserManager

import threading
import imp

class Bot():

    def __init__(self):
        self.botConfig = getConfig("conf/bot.conf")
        self.connection = SlackConnection(self.botConfig["authToken"])

        self.plugins = []
        self.event = EventManager()
        self.command = CommandManager()

        self.users = UserManager(self)

        # Initialize core events
        self.event.register("connection.login")
        self.event.register("connection.logout")
        self.event.register("send.message")
        self.event.register("plugin.exception")

        # Start Message Parser Thread
        self.messageParserThread = MessageParser(self)
        self.messageParserThread.daemon = True

    def login(self):
        self.connection.connect()
        self.messageParserThread.start()
        self.event.publish("connection.login")

    def logout(self):
        self.connection.disconnect()
        self.messageParserThread.join()
        self.event.publish("connection.logout")

    def say(self, message, channel="general"):
        self.connection.emit(channel, message)
        self.event.publish("send.message", message=message)

    def loadPlugins(self):
        for pluginName in self.botConfig["plugins"]:
            plugin = imp.load_source(pluginName, 'plugins/' + pluginName + ".py")

            if(plugin):
                pluginThread = plugin.init(self)
                self.plugins.append(pluginThread)
