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
        self.lastRequest = time.time()

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

    def request(self, method, request="?", headers=None, postData={}, domain="discordapp.com"):
        while(time.time() - self.lastRequest < 1):
            time.sleep(0.025)

        url = 'https://{}/api/{}'.format(domain, request)
        response = None

        if(method.lower() in ["post", "get", "delete", "head", "options", "put"]):
            self.lastRequest = time.time()
            response = requests.request(method.lower(), url, json=postData, headers=headers)
        else:
            raise Exception("Invalid HTTP request method")

        if(response.status_code not in range(200, 206)):
            raise Exception("API responded with HTTP code  " + str(response.status_code) + "\n\n" + response.text)
        else:
            if(response.text):
                returnData = json.loads(response.text)

                return returnData
            else:
                return None
