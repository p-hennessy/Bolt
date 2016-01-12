"""
    Class Name : MessageParser

    Description:
        Simple class to standardize message data

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""
import time
import shlex
import re

class messageType:
    MESSAGE = 0
    PRESSENCE = 1

class Envelope():
    def __init__(self, user, channel):
        self.sender = sender
        self.channel = channel

class Message():
    def __init__(self, type, senderID, channelID, content=None, senderNickname=None, timestamp=time.time()):
        self.type = type
        self.timestamp = timestamp
        self.sender = senderID
        self.senderNickname = senderNickname
        self.channel = channelID
        self.content = content
        self.match = None

    def asArgs(self):
        try:
            split = shlex.split(self.content)
        except ValueError:
            split = self.content.split(" ")

        return split

    def getMatches(self):
        if(self.match):
            return self.match.groups()

    def __call__(self):
        return Envelope(self.sender, self.channel)
