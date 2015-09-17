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
from core.Command import *
from core.Plugin import *

import threading

import plugins.Trivia
import plugins.Chat

class Bot():

    def __init__(self):
        self.token = "xoxb-6375106610-PiKFtyOj00bOBqTbaqCskYBb"
        self.trigger = "."

        self.connection = SlackConnection(self.token)

        self.commands = []
        self.commandLock = threading.Lock()

        self.plugins = []

        # Core events to subscribe to
        self.subscriptions = {}

        # Initialize core events
        self.registerEvent("connection.login")
        self.registerEvent("connection.logout")
        self.registerEvent("recieve.message")
        self.registerEvent("recieve.command")
        self.registerEvent("user.typing")
        self.registerEvent("user.pressence")
        self.registerEvent("send.message")
        self.registerEvent("plugin.exception")

        self.subscribe("plugin.exception", self.pluginCrash)

        self.messageThread = threading.Thread(target=self._parseMessageBuffer)
        self.messageThread.daemon = True

    def pluginCrash(self, args):
        print "Exception caught in thread: " + args['thread']
        exc_type, exc_obj, exc_trace = args['exception']
        traceback.print_exception(exc_type, exc_obj, exc_trace)

    def login(self):
        self.connection.connect()
        self.messageThread.start()

        self.publish("connection.login")

    def logout(self):
        self.connection.disconnect()
        self.messageThread.join()

        self.publish("connection.logout")

    def say(self, message, channel="general"):
        self.connection.emit(channel, message)

    def loadPlugins(self):
        myPlugin = plugins.Chat.init(self)

    def subscribe(self, event, callback):
        if(callback not in self.subscriptions[event]):
            self.subscriptions[event].append(callback)
            return True
        else:
            raise CoreSubscriptionError("Callback \"" + str(callback.__name__) + "\" was already subscribed to \"" + event + "\"")

    def unsubscribe(self, event, callback):
        if(callback in self.subscriptions[event]):
            self.subscriptions[event].remove(callback)
            return True
        else:
            raise CoreSubscriptionError("Callback \"" + str(callback.__name__) + "\" was not subscribed to \"" + event + "\"")

    def registerCommand(self, command):
        self.commands.append(command)

    def registerEvent(self, event):
        self.subscriptions[event] = []

    def _parseMessageBuffer(self):
        while self.connection.connected:
            messageBuffer = self.connection.consumeMessageBuffer()

            if(messageBuffer):
                for message in messageBuffer:
                    if not("type" in message.keys()):
                        continue

                    if(message["type"] == "message"):
                        if(message["text"].startswith(self.trigger)):
                            cmd = message["text"][1:].split(" ")[0]

                            for command in self.commands:
                                if(command.invocation == cmd):
                                    command.callback()

                            self.publish("recieve.command", text=message["text"], uid=message["user"], timestamp=message["ts"], channel=message["channel"])
                        else:
                            self.publish("recieve.message", text=message["text"], uid=message["user"], timestamp=message["ts"], channel=message["channel"])

    def publish(self, event, **kwargs):
        for callback in self.subscriptions[event]:
            callback(kwargs)

    def getUserInfo(self, uid):
        return self.connection.slackAPI.users.info(self.token, uid)

class CoreSubscriptionError(Exception):
    def __init__(self, msg):
        super(CoreSubscriptionError, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg
