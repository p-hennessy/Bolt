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
from platform import system
from ssl import *

import websocket
import socket
import threading
import time
import logging
import json
import random

from core.Connector import Connector
from core.Message import *

import requests

class Discord(Connector):
    def __init__(self, core, email, password):
        super(Discord, self).__init__()
        self.core = core
        self.logger = logging.getLogger("connector." + __name__)

        # Authentication / Connection Data
        self.email = email
        self.password = password
        self.uid = None                 # UID of bot so that it doesnt respond to itself

        self.userData = {}              # Caches data about users

        self.token = None               # Token used to authenticate api requests
        self.socket = None              # Websocket connection handler to Discord

        self.connected = False          # Boolean for handling connection state
        self.heartbeatInterval = 41250  # Time in ms between KeepAlive pings

        # Internal threads
        self.keepAliveThread = None
        self.messageConsumerThread = None

        # Events that this connector publishes
        self.core.event.register("connect")
        self.core.event.register("disconnect")
        self.core.event.register("message")
        self.core.event.register("pressence")

    def connect(self):
        # Connect to Discord, post login credentials
        self.logger.info("Attempting connection to Discord servers")

        try:
            tokenRequest = self.request("POST", "auth/login", postData={"email":self.email, "password":self.password})
            self.token = tokenRequest['token']
        except:
            return

        # Request a WebSocket URL
        socketURL = self.request("GET", "gateway", headers={"authorization": self.token})["url"]

        # Create socket connection
        self.socket = websocket.create_connection(socketURL)

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

        self.__writeSocket(initData)
        loginData = self.__readSocket()

        # Get self user id so to not respond to own messages
        self.uid = loginData["d"]["user"]["id"]

        # Set websocket to nonblocking so we can exit a thread reading from the socket if we need to
        self.socket.sock.setblocking(0)
        self.connected = True

        self.logger.info("Succesful login to Discord")
        self.core.event.notify('connect')

        # Create and start threads
        self.keepAliveThread = threading.Thread(target=self.__keepAlive, name="KeepAliveThread")
        self.keepAliveThread.daemon = True
        self.keepAliveThread.start()

        self.messageConsumerThread = threading.Thread(target=self.__messageConsumer, name="MessageConsumerThread")
        self.messageConsumerThread.daemon = True
        self.messageConsumerThread.start()

    def disconnect(self):
        self.core.event.notify('disconnect')
        self.connected = False

        # Join threads if they exist
        if( isinstance(self.keepAliveThread, threading.Thread) ):
            self.keepAliveThread.join()

        if( isinstance(self.messageConsumerThread, threading.Thread) ):
            self.messageConsumerThread.join()

        self.logger.debug('Joined MessageConsumer and KeepAlive threads')

        # Close websocket if it is established
        if( isinstance(self.socket, websocket.WebSocket)):
            self.socket.close()

        self.logger.info("Disconnected from Discord")

    def send(self, channel, message, mentions=[]):
        self.logger.debug("Sending message to channel " + channel)
        try:
            self.request("POST", "channels/{}/messages".format(channel), postData={"content": "{}".format(message), "mentions":mentions}, headers={"authorization": self.token})
        except:
            self.logger.warning('Send message to {} failed'.format(channel))

    def reply(self, envelope, message):
        self.logger.debug("Sending reply to " + envelope.sender)
        try:
            self.request("POST", "channels/{}/messages".format(envelope.channel), postData={"content": "<@{}> {}".format(envelope.sender, message), "mentions":[envelope.sender]}, headers={"authorization": self.token})
        except:
            self.logger.warning('Reply to {} failed'.format(envelope.sender))

    def whisper(self, sender, message):
        self.logger.debug("Whisper to " + message.sender)

    def getUsers(self):
        pass

    def getUser(self, userID):
        if(userID in self.userData and self.userData[userID]['expires'] < time.time()):
            return self.userData[userID]
        else:
            user = self.request("GET", "users/{}".format(userID), headers={"authorization": self.token})
            self.userData[userID] = user

            return {
                'name': user['username'],
                'id': user['id'],
                'expires': time.time() + 600
            }

    # Thread Methods
    def __keepAlive(self):
        self.logger.debug("Spawning keepAlive thread at interval: " + str(self.heartbeatInterval))

        startTime = time.time()

        while self.connected:
            now = time.time()

            if((now - startTime) >= (self.heartbeatInterval/1000) - 1):
                self.__writeSocket({"op":1,"d": time.time()})
                self.logger.debug("KeepAlive")

                startTime = time.time()

            time.sleep(1)

    def __messageConsumer(self):
        self.logger.debug("Spawning messageConsumer thread")

        while self.connected:
            # Sleep is good for the body; also so we don't hog the CPU polling the socket
            time.sleep(0.5)

            # Read data off of socket
            rawMessage = self.__readSocket()
            if not rawMessage: continue

            # Parse raw message
            message = self.__parseMessageData(rawMessage)
            if not message: continue

            # Have worker thread take it from here
            self.core.threadPool.queueTask(self.__handleMessage, message)

    # Handler Methods
    def __handleMessage(self, message):
        # If incoming message is a MESSAGE text
        if(message.type == messageType.MESSAGE):
            self.core.event.notify("message",  message=message)
            self.core.command.checkMessage(message)

        # If incoming message is PRESSENCE update
        elif(type == messageType.PRESSENCE):
            self.core.event.notify("pressence", message=message)

    def __handleInteruption(self):
        self.connected = False
        self.disconnect()
        self.connect()

    # Socket Methods
    def __writeSocket(self, data):
        try:
            self.socket.send(json.dumps(data))
        except socket_error as e:
            if e.errno == 104:
                if not self.connected:
                    return

                self.logger.warning("Connection reset by peer")
                self.core.threadPool.queueTask(self.__handleInteruption)
            else:
                raise
        except websocket.WebSocketConnectionClosedException:
            self.logger.warning("Websocket unexpectedly closed; attempting reconnection.")
            self.core.threadPool.queueTask(self.__handleInteruption)

    def __readSocket(self):
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
                    if not self.connected:
                        return

                    self.logger.warning("Connection reset by peer")
                    self.core.threadPool.queueTask(self.__handleInteruption)
                    return None

                # Raised when send buffer is full; we must try again
                if e.errno == 11:
                    return None
                raise
            except websocket.WebSocketConnectionClosedException:
                self.logger.warning("Websocket unexpectedly closed; attempting reconnection.")
                self.core.threadPool.queueTask(self.__handleInteruption)

    # Parser Methods
    def __parseMessageData(self, message):
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
