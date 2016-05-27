"""
    Class Name : Message

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
import re

class messageType:
    MESSAGE = 0
    PRESSENCE = 1

class Message():
    def __init__(self, type, sender_id, channel_id, content="", mentions=[], sender_name=None, timestamp=time.time()):
        self.type = type
        self.timestamp = timestamp
        self.sender = sender_id
        self.sender_name = sender_name
        self.channel = channel_id
        self.content = content
        self.mentions = mentions

        self._match_obj = None
        self._match = None

    @property
    def arguments(self):
        if(self._match_obj):
            return self._match_obj.groups()
        else:
            return []

    @arguments.setter
    def arguments(self, match):
        self._match_obj = match
        self._match = match.groups()

    def __call__(self):
        return (self.sender, self.channel)
