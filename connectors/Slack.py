"""
    Class Name : Slack Connector

    Description:
        Low-level communication interface between the bot core and the chat server
        This connector is intended for Slack.com
        It MUST subclass the abstract Connector class for consistancy and interoperability

    Contributors:
        - Patrick Hennessy

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

import requests

from core.Connector import Connector
from core.Message import *

class Slack(Connector):
    def __init__(self, core, token):
        super(Slack, self).__init__()
        self.core = core
        self.logger = logging.getLogger("connector." + __name__)

        # Authentication / Connection Data
        self.uid = None                 # UID of bot so that it doesnt respond to itself
        self.token = token              # Token used to authenticate api requests
        self.socket = None              # Websocket connection handler to Slack RTM

        self.connected = False          # Boolean for handling connection state

        # Internal threads
        self.messageConsumerThread = None

        # Events that this connector publishes
        self.core.event.register("connect")
        self.core.event.register("disconnect")
        self.core.event.register("message")
        self.core.event.register("pressence")

    def connect(self):
        # Connect to Discord, post login credentials
        self.logger.info("Attempting connection to Slack")

        #rtmStart = requests.request("post", "https://slack.com/api/rtm.start", json={"token": self.token})
        rtmStart = self.request("POST", "rtm.start", postData={"token": self.token}, domain="slack.com")

        if(rtmStart["ok"]):
            self.socket = websocket.create_connection(rtmStart["url"])
            self.socket.sock.setblocking(0)

            self.connected = True

            self.logger.info("Succesful login to Slack")
            self.core.event.notify('connect')

        else:
            self.logger.critical("Unable to login to Slack server")
            return

        # Create and start threads
        self.messageConsumerThread = threading.Thread(target=self.__messageConsumer, name="MessageConsumerThread")
        self.messageConsumerThread.daemon = True
        self.messageConsumerThread.start()

    def disconnect(self):
        self.core.event.notify('disconnect')
        self.connected = False

        # Join threads if they exist
        if( isinstance(self.messageConsumerThread, threading.Thread) ):
            self.messageConsumerThread.join()

        self.logger.debug('Joined MessageConsumer thread')

        # Close websocket if it is established
        if( isinstance(self.socket, websocket.WebSocket)):
            self.socket.close()

    def send(self, channel, message, mentions=[]):
        self.logger.debug("Sending message to channel " + channel)

        self.__writeSocket({
            "id": 1,
            "type": "message",
            "channel": channel,
            "text": message
        })

    def reply(self, envelope, message):
        self.logger.debug("Sending reply to " + envelope.sender)

        self.__writeSocket({
            "id": 1,
            "type": "message",
            "channel": envelope.channel,
            "text": message
        })

    def whisper(self, user, message):
        self.logger.debug("Whisper to " + user)

        response = self.request("POST", "im.open", postData={"token": self.token, "user": user}, domain="slack.com")

        if not(response["ok"]):
            self.logger.warning("Failed to send message to {}".format(user))
            return

        channel = response["channel"]["id"]

        self.__writeSocket({
            "id": 1,
            "type": "message",
            "channel": channel,
            "text": message
        })

    def getUsers(self):
        pass

    def getUser(self, userID):
        user = self.request("POST", "users.info", postData={"token": self.token, "user": userID}, domain="slack.com")

        return {
            'name': user['user']['name'],
            'id': user['user']['id']
        }

    def __messageConsumer(self):
        self.logger.debug("Spawning messageConsumer thread")

        while self.connected:
            # Sleep is good for the body; also so we don't hog the CPU polling the socket
            time.sleep(0.01)

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

    # Parser Methods
    def __parseMessageData(self, message):
        type = content = sender = channel = content = timestamp = None

        if not("type" in message):
            return

        if(message["type"] == "message"):
            type = messageType.MESSAGE
            sender = message["user"]
            channel = message["channel"]
            content = message["text"]

        else:
            with open('unhandled_messages.txt', "a+") as file:
                file.write(json.dumps(message))

            return None

        if(sender == self.uid):
            return None

        return Message(type, sender, channel, content, timestamp=time.time())
