#!/usr/bin/python

from lib.SlackClient import *
from lib.MessageParser import *
import threading

import plugins.Trivia
import plugins.Chat

class Bot():

    def __init__(self):
        self.token = "xoxb-6375106610-PiKFtyOj00bOBqTbaqCskYBb"
        self.connection = SlackConnection(self.token)

        self.trigger = "."

        self.commands = []
        self.commandLock = threading.Lock()

        self.plugins = []

        # Core events to subscribe to
        self.subscriptions = {
            "connection.login"  : [],
            "connection.logout" : [],
            "recieve.message"   : [],
            "recieve.command"   : [],
            "user.typing"       : [],
            "user.pressence"    : [],
            "send.message"      : []
        }

        self.messageThread = threading.Thread(target=self._parseMessageBuffer)
        self.messageThread.daemon = True

    def login(self):
        self.connection.connect()
        self.messageThread.start()

    def logout(self):
        self.connection.disconnect()
        self.messageThread.join()

    def say(self, message, channel="general"):
        self.connection.emit(channel, message)

    def loadPlugins(self):
        self.plugins.append( plugins.Chat.init(self) )

    def subscribe(self, event, callback):
        if(callback not in self.subscriptions[event]):
            self.subscriptions[event].append(callback)
            return True
        else:
            raise BotSubscriptionError("Callback \"" + str(callback.__name__) + "\" was already subscribed to \"" + event + "\"")

    def unsubscribe(self, event, callback):
        if(callback in self.subscriptions[event]):
            self.subscriptions[event].remove(callback)
            return True
        else:
            raise BotSubscriptionError("Callback \"" + str(callback.__name__) + "\" was not subscribed to \"" + event + "\"")

    def registerCommand(self, command):
        self.commands.append(command)

    def _parseMessageBuffer(self):
        while self.connection.connected:

            messageBuffer = self.connection.consumeMessageBuffer()

            if(messageBuffer):
                for message in messageBuffer:
                    #print message
                    if not("type" in message.keys()):
                        return

                    if(message["type"] == "message"):
                        if(message["text"].startswith(self.trigger)):
                            cmd = message["text"][1:].split(" ")[0]

                            for command in self.commands:
                                if(command.invocation == cmd):
                                    command.callback()

                            self._publish("recieve.command", text=message["text"], uid=message["user"], timestamp=message["ts"], channel=message["channel"])
                        else:
                            self._publish("recieve.message", text=message["text"], uid=message["user"], timestamp=message["ts"], channel=message["channel"])

    def _publish(self, event, **kwargs):
        for callback in self.subscriptions[event]:
            callback(kwargs)

    def getUserInfo(self, uid):
        return self.connection.slackAPI.users.info(self.token, uid)

class BotSubscriptionError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
