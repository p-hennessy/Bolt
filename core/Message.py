"""
    Class Name : MessageParser

    Description:
        Simple class to standardize message data

    Contributors:
        - Patrick Hennessy

    License:
        PhilBot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""
import datetime

class Message():

    def __init__(self, sender, channel, timestamp, text, mention=None):
        self.sender = sender
        self.channel = channel
        self.timestamp = timestamp
        self.text = text
        self.mention = mention
