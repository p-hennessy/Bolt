"""
    Class Name : Discord Connector

    Description:
        Provides functionality for connecting to Discord chat server
        This class is a subclass of core/Connector.py and implements the
            required methods so the rest of the bot can talk to Discord

    Contributors:
        - Patrick Hennessy
        - Aleksandr Tihomirov

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from __future__ import print_function

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
        super(Discord, self).__init__()
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
            "v": 3
        }

        self.writeSocket(initData)
        self.loginData = self.readSocket()

        self.uid = self.loginData["d"]["user"]["id"]

        # Set websocket to nonblocking
        self.socket.sock.setblocking(1)
        self.connected = True

        self.logger.info("Succesful login to Discord")
        self.core.event.notify('connect')

        self.keepAliveThread = threading.Thread(target=self.keepAlive, name="KeepAliveThread")
        self.keepAliveThread.daemon = True
        self.keepAliveThread.start()

        self.messageConsumerThread = threading.Thread(target=self.messageConsumer, name="MessageConsumerThread")
        self.messageConsumerThread.daemon = True
        self.messageConsumerThread.start()

    def disconnect(self):
        self.core.event.notify('disconnect')
        self.connected = False

        self.keepAliveThread.join()
        self.messageConsumerThread.join()

        self.socket.close()
        self.logger.info("Disconnected from Discord")

    def send(self, channel, message, mentions=[]):
        self.logger.debug("Sending message to channel " + channel)
        self.api.channels.send(self.token, channel, "{}".format(message))

    def reply(self, envelope, message):
        self.logger.debug("Sending reply to " + envelope.sender)
        self.api.channels.send(self.token, envelope.channel, "<@{}> {}".format(envelope.sender, message), mentions=[envelope.sender])

    def whisper(self, sender, message):
        self.logger.debug("Whisper to " + message.sender)

    def getUsers(self):
        pass

    def getUser(self, userID):
        pass

    def messageConsumer(self):
        self.logger.debug("Spawning messageConsumer thread")

        while self.connected:
            # Sleep is good for the body; also so we don't hog the CPU polling the socket
            time.sleep(0.5)

            # Read data off of socket
            rawMessage = self.readSocket()
            if not rawMessage: continue

            # Parse raw message
            message = self.parseMessageData(rawMessage)
            if not message: continue

            self.core.threadPool.queueTask(self.handleMessage, message)

    def handleMessage(self, message):
        # If incoming message is a MESSAGE text
        if(message.type == messageType.MESSAGE):
            self.core.event.notify("message",  message=message)
            self.core.command.check(message)

        # If incoming message is PRESSENCE update
        elif(type == messageType.PRESSENCE):
            self.core.event.notify("pressence", message=message)

    def keepAlive(self):
        self.logger.debug("Spawning keepAlive thread at interval: " + str(self.heartbeatInterval))

        startTime = time.time()

        while self.connected:
            now = time.time()

            if((now - startTime) >= (self.heartbeatInterval/1000) - 1):
                self.writeSocket({"op":1,"d": time.time()})
                self.logger.debug("KeepAlive")

                startTime = time.time()

            time.sleep(0.5)

    def writeSocket(self, data):
        try:
            self.socket.send(json.dumps(data))
        except socket_error as e:
            if e.errno == 104:
                self.logger.warning("Connection reset by peer")
                self.core.threadPool.queueTask(self.handleInteruption)
                self.connected = False
        except websocket.WebSocketConnectionClosedException:
            self.logger.warning("Websocket unexpectedly closed; attempting reconnection.")
            self.core.threadPool.queueTask(self.handleInteruption)
            self.connected = False

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
                continue
            except SSLError as e:
                # Raised when we can't read the entire buffer at once
                if e.errno == 2:
                    return None
                raise
            except socket_error as e:
                # Raised when connection reset by peer
                if e.errno == 104:
                    self.logger.warning("Connection reset by peer")
                    self.core.threadPool.queueTask(self.handleInteruption)
                    self.connected = False

                    return None

                # Raised when send buffer is full; we must try again
                if e.errno == 11:
                    return None
                raise

    def handleInteruption(self):
        self.disconnect()
        self.connect()

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
            with open('unhandled_messages.txt', "a+") as file:
                file.write(json.dumps(message))

            return None

        if(sender == self.uid):
            return None

        return Message(type, sender, channel, content, timestamp=time.time())

    def parseLoginData(self, data):
        self.users = {}
        self.servers = {}
        self.channels = {}
        self.heartbeatInterval = data["d"]["heartbeat_interval"]

        print(json.dumps(data))

        for guild in data["d"]["guilds"]:
            guildID = guild['id']

            print(json.dumps(guild))

            self.servers[guildID] = []

            for channel in guild["channels"]:
                print(channel)






# Super class for all API calls
class _api():
    def __init__(self):
        pass

    def request(self, method, request="?", token=None, postData={}, domain="discordapp.com"):
        headers={"authorization": token}

        url = 'https://{}/api/{}'.format(domain, request)

        if(method.lower() in ["post", "get", "delete", "head", "options", "put"]):
            response = requests.request(method.lower(), url, json=postData, headers=headers)
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
    def info(self, token, userID):
        return self.request("GET", "users/" + userID, token)

class gateway(_api):
    def __call__(self, token):
        return self.request("GET", "gateway", token)

class channels(_api):
    def info(self, token, channelID):
        return self.request("GET", "channels/" + channelID, token)

    def send(self, token, channelID, content, mentions=[]):
        return self.request("POST", "channels/" + channelID + "/messages", postData={"content": content, "mentions":mentions}, token=token)

    def directMessage(self, token):
        pass

    def typing(self, token, channelID):
        return self.request("POST", "channels/" + channelID + "/typing", token)

class guilds(_api):
    def info(self, token, serverID):
        return self.request("GET", "guilds/" + serverID, token)

    def members(self, token, serverID):
        return self.request("GET", "guilds/" + serverID + "/members", token)

    def createChannel(self, token, serverID, channelName, type):
        return self.request("POST", "guilds/" + serverID + "/channels", token, postData={"name":channelName, "type": type})

    def channels(self, token, serverID):
        return self.request("GET", "guilds/" + serverID + "/channels", token)

class voice(_api):
    def regions(self):
        self.request("GET", "voice/regions", token)
