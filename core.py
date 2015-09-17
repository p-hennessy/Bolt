#!/usr/bin/python

from lib.SlackClient import *


class Bot():

    def __init__(self):
        self.token = "xoxb-6375106610-PiKFtyOj00bOBqTbaqCskYBb"
        self.connection = SlackConnection(self.token)

    def login(self):
        self.connection.connect()

    def logout(self):
        self.connection.disconnect()

    def say(self, message, channel="general"):
        self.connection.emit(channel, message)

    def whisper(self):
        pass

    def parse(self):
        msg = self.connection.getMessages()

        if(msg):
            for item in msg:
                print item
