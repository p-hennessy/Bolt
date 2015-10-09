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

class Plugin(object):
    def __init__(self, core, name):

        # Expose core and plugin name for subclasses
        self.core = core
        self.name = name
        self.database = self.core.database

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
                Will send a message in channel that is directed at the user

            Args:
                envelope (Envelope): An object containing information about the sender and channel it came from
                message (str): String form of message to send to channel

            Returns:
                None
        """
        self.core.connection.reply(envelope, message)

    def say(self, channel, message):
        """
            Summary:
                Wrapper method calling the connection's send method
                Sends a message to a channel

            Args:
                channel (str): Channel id to send message to
                message (str): String form of message to send to channel

            Returns:
                None
        """
        self.core.connection.send(channel, message)

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
        pass
