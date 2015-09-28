"""
    Class Name : Connector

    Description:
        Abstract class for which all backend connectors must derive

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from abc import *

class Connector():
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def send(self, envelope, message, mentions=[]):
        pass

    @abstractmethod
    def reply(self, envelope, message):
        pass

    @abstractmethod
    def whisper(self, envelope, message):
        pass

    @abstractmethod
    def getUsers(self):
        pass

    @abstractmethod
    def getUser(self, userID):
        pass
