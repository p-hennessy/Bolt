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
import requests
import json
import time

class Connector():
    __metaclass__ = ABCMeta

    def __init__(self):
        self.last_request = time.time()

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def say(self, channel, message, mentions=[]):
        pass

    @abstractmethod
    def reply(self, user, channel, message):
        pass

    @abstractmethod
    def whisper(self, user, message):
        pass

    @abstractmethod
    def upload(self, channel, file):
        pass

    def rate_limit_lock():
        pass
