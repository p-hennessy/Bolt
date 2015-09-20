"""
    Class Name : Connector

    Description:
        Abstract class for which all backend connectors must derive

    Contributors:
        - Patrick Hennessy

    License:
        PhilBot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from abc import *

class Connector():
    __metaclass__ = ABCMeta

    _connected = False
    _messageBuffer = None

    def __init__(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def ping(self):
        """
            Purpose
                - Send packet to server to check connection
            Arguments
                - None
            Returns
                - Integer
                - Time in milliseconds it took to reach the server
                - If cannot reach server; raise exception
        """
        pass

    @abstractmethod
    def send(self, message):
        pass

    @abstractmethod
    def whisper(self, userID, message):
        pass

    @abstractmethod
    def recieve(self):
        pass

    @abstractmethod
    def getUsers(self):
        pass

    @abstractmethod
    def getUser(self, userID):
        pass

    @abstractmethod
    def getChannels(self):
        pass

    @abstractmethod
    def getChannel(self, channelID):
        pass
