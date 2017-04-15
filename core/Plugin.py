"""
    Class Name : Plugin

    Description:
        Superclass for which all plugins are derived

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import logging
from core.Database import *

class Plugin(object):
    def __init__(self, core, name):

        # Expose core and plugin name for subclasses
        self.core = core
        self.name = name
        self.database = Database(databaseName="databases/" + self.name + ".db")

        # Expose logger for subclasses
        self.logger = logging.getLogger("plugins." + self.name)

    def activate(self):
        """
            Summary:
                This method is invoked when a plugin is first loaded

            Args:
                None

            Returns:
                None
        """
        pass

    def deactivate(self):
        """
            Summary:
                This method is invoked when a plugin is disabled.
                Should be any nessessary garbage collection

            Args:
                None

            Returns:
                None
        """
        pass

    # Exposed methods for Plugin use
    def reply(self, envelope, message):
        """
            Summary:
                Wrapper method calling the connection's reply method
                Will send a message in channel that is directed at the user who invoked the command

            Args:
                envelope (tuple): An object containing information about the sender and channel it came from
                message (str): String form of message to send to channel

            Returns:
                None
        """
        self.core.connection.reply(envelope.sender, envelope.channel, message)

    def say(self, channel, message, embed={}, mentions=[]):
        """
            Summary:
                Wrapper method calling the connection's send method
                Sends a message to a channel

            Args:
                channel (str): Channel id to send message to
                message (str): String form of message to send to channel
                mentions (list): List of users to mention in a channel

            Returns:
                None
        """
        self.core.connection.say(channel, message, mentions=mentions)

    def whisper(self, user, message):
        """
            Summary:
                Wrapper method calling the connection's whisper method
                Will send a private message that only the recipent can see

            Args:
                user (str): UserId of the intended recipent
                message (str): String form of message to send to channel

            Returns:
                None
        """
        self.core.connection.whisper(user, message)

    def upload(self, channel, file):
        """
            Summary:
                Wrapper method calling the connection's upload method
                Uploads a file to a channel

            Args:
                channel (str): Channel id to send message to
                file (str): Path of file to upload

            Returns:
                None
        """
        self.core.connection.upload(channel, file)
