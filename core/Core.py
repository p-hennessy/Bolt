"""
    Class Name : Core

    Description:
        Provides an extensible engine for plugins to interact with
        Features:
            - Publish / Subscribe Event System
            - Plugin manager
            - Configuration manager
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
from core.Command import Command
from core.Command import CommandManager
from core.Event import EventManager

import threading
import imp

class Bot():

    def __init__(self):
        self.botConfig = getConfig("conf/bot.conf")
        self.connection = SlackConnection(self.botConfig["authToken"])

        self.plugins = []
        self.event = EventManager()
        self.command = CommandManager()

        # Initialize core events
        self.event.register("connection.login")
        self.event.register("connection.logout")
        self.event.register("recieve.message")
        self.event.register("recieve.command")
        self.event.register("send.message")
        self.event.register("plugin.exception")

        self.messageThread = threading.Thread(target=self._parseMessageBuffer)
        self.messageThread.daemon = True

    def login(self):
        self.connection.connect()
        self.messageThread.start()

        self.event.publish("connection.login")

    def logout(self):
        self.connection.disconnect()
        self.messageThread.join()

        self.event.publish("connection.logout")

    def say(self, message, channel="general"):
        self.connection.emit(channel, message)

    def loadPlugins(self):
        for pluginName in self.botConfig["plugins"]:
            plugin = imp.load_source(pluginName, 'plugins/' + pluginName + ".py")
            pluginThread = plugin.init(self)

            self.plugins.append(pluginThread)

    def _parseMessageBuffer(self):
        while self.connection.connected:
            messageBuffer = self.connection.consumeMessageBuffer()

            if(messageBuffer):
                for message in messageBuffer:
                    if not("type" in message.keys()):
                        continue

                    if(message["type"] == "message"):
                        if(message["text"].startswith(self.botConfig["trigger"])):
                            cmd = message["text"][1:].split(" ")[0]
                            self.command.invoke(str(cmd))

                            self.event.publish("recieve.command", text=message["text"], uid=message["user"], timestamp=message["ts"], channel=message["channel"])
                        else:
                            self.event.publish("recieve.message", text=message["text"], uid=message["user"], timestamp=message["ts"], channel=message["channel"])


    def getUserInfo(self, uid):
        return self.connection.slackAPI.users.info(self.botConfig["authToken"], uid)
