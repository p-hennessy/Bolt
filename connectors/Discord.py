#! /usr/bin/python2.7

import requests
import json
import websocket
import socket
import time
from ssl import *
import sys
import threading
import random
import logging
import datetime

from platform import system

from core.Connector import Connector
from core.Message import *

class Discord(Connector):
    def __init__(self, core, email, password):
        self.core = core
        self.logger = logging.getLogger("connector." + __name__)

        self.email = email
        self.password = password

        self.token = None
        self.api = DiscordAPI()

        self.socketURL = None
        self.socket = None
        self.connected = False

        self.heartbeatInterval = 41250
        self.keepAliveThread = None
        self.messageConsumerThread = None

        self.core.event.register("connect")
        self.core.event.register("connectionInterupted")
        self.core.event.register("disconnect")
        self.core.event.register("message")
        self.core.event.register("pressence")

    def connect(self):
        # Connect to Discord, post login credentials
        self.logger.info("Attempting connection to Discord servers")
        login = self.api.auth.login(self.email, self.password)
        self.token = login["token"]

        # Request a WebSocket URL
        loginWS = self.api.gateway(self.token)
        self.socketURL = loginWS["url"]

        # Create socket connection
        self.socket = websocket.create_connection(self.socketURL)

        # Immediately pass message to server about your connection
        initData = {
            "op": 2,
            "d": {
                "token": self.token,
                "properties": {
                    "$os": system(),
                    "$browser":"",
                    "$device":"Python",
                    "$referrer":"",
                    "$referring_domain":""
                },
            },
            "v": 2
        }

        self.writeSocket(initData)
        self.loginData = self.readSocket()

        # Set websocket to nonblocking
        self.socket.sock.setblocking(0)
        self.connected = True

        self.logger.info("Succesful login to Discord")

        self.keepAliveThread = threading.Thread(target=self.keepAlive, name="KeepAliveThread")
        self.keepAliveThread.daemon = True
        self.keepAliveThread.start()

        self.messageConsumerThread = threading.Thread(target=self.messageConsumer, name="MessageConsumerThread")
        self.messageConsumerThread.daemon = True
        self.messageConsumerThread.start()

    def disconnect(self):
        self.connected = False
        self.socket.close()

    def send(self, envelope, message):
        pass

    def emote(self, envelope, message):
        pass

    def reply(self, envelope, message):
        self.logger.debug("Sending reply to " + envelope.sender)
        self.api.channels.send(self.token, envelope.channel, "<@{}> {}".format(envelope.sender, message), mentions=[envelope.sender])

    def whisper(self, envelope, message):
        pass

    def getUsers(self):
        pass

    def getUser(self, userID):
        pass

    def messageConsumer(self):
        self.logger.debug("Spawning messageConsumer thread")

        while self.connected:
            time.sleep(0.1)

            # Read data off of socket
            rawMessage = self.readSocket()
            if not rawMessage: continue

            # Parse raw message
            message = self.parseMessageData(rawMessage)
            if not message: continue

            # If incoming message is a MESSAGE text
            if(message.type == messageType.MESSAGE):
                self.core.event.notify("message",  message=message)

                if(message.content.startswith(self.core.config.trigger)):
                    message.content = message.content[1:]
                    self.core.command.check(message)

            # If incoming message is PRESSENCE update
            elif(type == messageType.PRESSENCE):
                self.core.event.notify("pressence", message=message)

    def keepAlive(self):
        self.logger.debug("Spawning keepAlive thread at interval: " + str(self.heartbeatInterval))

        while self.connected:
            time.sleep((self.heartbeatInterval / 1000) - 1)
            self.writeSocket({"op":1,"d": time.time()})
            self.logger.debug("KeepAlive")

    def writeSocket(self, data):
        self.socket.send(json.dumps(data))

    def readSocket(self):
        data = ""
        while True:
            try:
                data += self.socket.recv()

                if(data):
                    return json.loads(data.rstrip())
                else:
                    return None

            except ValueError as e:
                print "0"
                return None
            except SSLError as e:
                # Raised when we can't read the entire buffer at once
                if e.errno == 2:
                    return None
                raise
            except socket_error as e:
                # Raised when send buffer is full; we must try again
                if e.errno == 11:
                    return None
                raise

    def parseMessageData(self, message):
        type = content = sender = channel = content = timestamp = None

        if(message["t"] == "MESSAGE_CREATE"):
            type = messageType.MESSAGE
            sender = message["d"]["author"]['id']
            channel = message['d']['channel_id']
            content = message["d"]["content"]

        elif(message["t"] == "TYPING_START"):
            type = messageType.PRESSENCE
            sender = message["d"]["user_id"]
            channel = message['d']['channel_id']

        else:
            print message
            return None

        return Message(type, sender, channel, content, timestamp=time.time())


    def parseLoginData(self, data):

        self.users = {}
        self.servers = []
        self.channels = {}
        self.heartbeatInterval = data["d"]["heartbeat_interval"]

        for guild in data["d"]["guilds"]:

            newServer = Server(
                guild["id"],
                guild["name"]
            )

            for channel in guild["channels"]:
                if(channel["type"] == "text"):
                    newChannel = Channel(
                        channel["id"],
                        channel["name"]
                    )

                    newServer.addChannel(newChannel)

            self.servers.append(newServer)

            for member in guild["members"]:
                newUser = User(
                    member["user"]["id"],
                    member["user"]["username"]
                )

                if member["user"]["id"] in self.users:
                    continue
                else:
                    self.users[ member["user"]["id"] ] = newUser



# Super class for all API calls
class _api():
    def __init__(self):
        pass

    def request(self, method, request="?", token=None, postData={}, domain="discordapp.com"):
        headers={"authorization": token}

        url = 'http://{}/api/{}'.format(domain, request)

        if(method == "POST"):
            response = requests.post(url, json=postData, headers=headers)
        elif(method == "GET"):
            response = requests.get(url, postData, headers=headers)
        elif(method == "DELETE"):
            response = requests.delete(url, postData, headers=headers)
        elif(method == "HEAD"):
            response = requests.head(url, postData, headers=headers)
        elif(method == "OPTIONS"):
            response = requests.options(url, postData, headers=headers)
        elif(method == "PUT"):
            response = requests.put(url, postData, headers=headers)
        else:
            raise Exception("Invalid HTTP request method")

        if(response.status_code not in range(200, 206)):
            raise Exception("API responded with HTTP code  " + str(response.status_code) )
        else:
            if(response.text):
                returnData = json.loads(response.text)

                return returnData
            else:
                return None

class DiscordAPI():
    def __init__(self):
        self.users = users()
        self.gateway = gateway()
        self.channels = channels()
        self.guilds = guilds()
        self.auth = auth()
        self.voice = voice()

class auth(_api):
    def login(self, email, password):
        return self.request("POST", "auth/login", postData={"email":email, "password":password})

    def logout(self, token):
        return self.request("POST", "auth/logout", token)

class users(_api):
    def __init__(self):
        pass

    def info(self, token, userID):
        return self.request("GET", "users/" + userID, token)

class gateway(_api):
    def __init__(self):
        pass

    def __call__(self, token):
        return self.request("GET", "gateway", token)

class channels(_api):
    def __init__(self):
        pass

    def info(self, token, channelID):
        return self.request("GET", "channels/" + channelID, token)

    def send(self, token, channelID, content, mentions=[]):
        return self.request("POST", "channels/" + channelID + "/messages", postData={"content": content, "mentions":mentions}, token=token)

    def typing(self, token, channelID):
        return self.request("POST", "channels/" + channelID + "/typing", token)

class guilds(_api):
    def __init__(self):
        pass

    def info(self, token, serverID):
        return self.request("GET", "guilds/" + serverID, token)

    def members(self, token, serverID):
        return self.request("GET", "guilds/" + serverID + "/members", token)

    def channels(self, token, serverID):
        return self.request("GET", "guilds/" + serverID + "/channels", token)

class voice(_api):
    def __init__(self):
        pass

    def regions(self):
        self.request("GET", "voice/regions", token)