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

class Message():

    def __init__(self, senderID, channelID, timestamp, message, mention=None):
        self.sender = senderID
        self.channel = channelID
        self.timestamp = timestamp
        self.message = message
        self.mention = mention
