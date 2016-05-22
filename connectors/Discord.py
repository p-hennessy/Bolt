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

from platform import system
from ssl import *

import base64
import json
import logging
import random
import requests
import socket
import time
import threading
import websocket

from core.Connector import Connector
from core.Message import *

class Discord(Connector):
    def __init__(self, core, token):
        super(Discord, self).__init__()
        self.core = core
        self.logger = logging.getLogger("connector." + __name__)
        self.name = __name__

        # Authentication / Connection Data
        self.connectorCache = {
            "heartbeat_interval": 41250,
            "session_id":"",
            "self":{},
            "private_channels":[],
            "guilds":[]
        }

        self.token = token               # Token used to authenticate api requests
        self.socket = None               # Websocket connection handler to Discord
        self.connected = False           # Boolean for handling connection state

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

        # Request a WebSocket URL
        socketURL = self.request("GET", "gateway", headers={"authorization": self.token})["url"]

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
            "v": 4
        }

        self.__writeSocket(initData)
        self.__parseLoginData(self.__readSocket())

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
            self.logger.warning('Send message to channel \'{}\' failed'.format(channel))

    def reply(self, envelope, message):
        self.logger.debug("Sending reply to " + envelope.sender)
        try:
            self.request("POST", "channels/{}/messages".format(envelope.channel), postData={"content": "<@{}> {}".format(envelope.sender, message), "mentions":[envelope.sender]}, headers={"authorization": self.token})
        except:
            self.logger.warning('Reply to user \'{}\' in channel \'{}\' failed'.format(envelope.sender, envelope.channel))

    def whisper(self, user, message):
        for channel in self.connectorCache['private_channels']:
            if channel['recipient']['id'] == user:
                self.send(channel['id'], message)
                break
        else:
            channel = self.request("POST", "users/@me/channels", postData={"recipient_id": "{}".format(user)}, headers={"authorization": self.token})
            self.connectorCache['private_channels'].append(channel)
            self.send(channel['id'], message)

        self.logger.debug("Whisper to " + user)

    def upload(self, channel, file):
        self.logger.debug('Sending file to channel ' + channel)

        files = {'file': open(file, 'rb')}

        try:
            self.request('POST', "channels/{}/messages".format(channel),  files=files, headers={"authorization": self.token})
        except:
            self.logger.warning('Upload file \'{}\' to channel {} failed'.format(file, channel))

    def getUsers(self):
        pass

    def getUser(self, userID):
        user = self.request("GET", "users/{}".format(userID), headers={"authorization": self.token})

        return {
            'name': user['username'],
            'id': user['id'],
            'expires': time.time() + 600
        }

    # Discord Specific
    def leaveGuild(self, guild_id):
        self.request("DELETE", "users/@me/guilds/{}".format(guild_id), headers={"authorization": self.token})

    def getServers(self):
        return self.request("GET", "users/@me/guilds", headers={"authorization": self.token})

    # User Management
        # Set roles
        # Ban
        # Sync Roles
    # Channel Management
        # Add / remove Channel
        # Apply premissions to Channel

    def gatherFacts(self):

        self.connectorDict['self'] = self.request("GET", "users/@me", headers={"authorization": self.token})
        self.connectorDict['direct_messages'] = self.request("GET", "users/@me/channels", headers={"authorization": self.token})
        self.connectorDict['guilds'] = self.request("GET", "users/@me/guilds", headers={"authorization": self.token})

        print(json.dumps(self.connectorDict))

    def setAvatar(self):
        with open("conf/avatar.png", "rb") as avatarImage:
            rawImage = avatarImage.read()

        raw = base64.b64encode(rawImage)
        with open("test", "wb") as file:
            file.write(raw)

        return

        self.request("PATCH", "users/@me", postData={"username": "Arcbot", "avatar": "data:image/png;base64," + base64.b64encode(rawImage).decode('ascii')}, headers={"authorization": self.token})

    # Thread Methods
    def __keepAlive(self):
        self.logger.debug("Spawning keepAlive thread at interval: " + str(self.connectorCache['heartbeat_interval']))

        startTime = time.time()

        while self.connected:
            now = time.time()

            if((now - startTime) >= (self.connectorCache['heartbeat_interval']/1000) - 1):
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

    # Socket Methods
    def __writeSocket(self, data):
        try:
            self.socket.send(json.dumps(data))
        except socket_error as e:
            if e.errno == 104:
                if not self.connected:
                    return

                self.logger.warning("Connection reset by peer.")
                self.connected = False

            else:
                raise
        except websocket.WebSocketConnectionClosedException:
            self.logger.warning("Websocket unexpectedly closed.")
            self.connected = False

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

                    self.logger.warning("Connection reset by peer.")
                    self.connected = False
                    return None

                # Raised when send buffer is full; we must try again
                if e.errno == 11:
                    return None
                raise
            except websocket.WebSocketConnectionClosedException:
                self.logger.warning("Websocket unexpectedly closed.")
                self.connected = False

    # Parser Methods
    def __parseMessageData(self, message):
        type = content = sender = senderNickname = channel = content = timestamp = None

        if(message["t"] == "MESSAGE_CREATE"):
            type = messageType.MESSAGE
            sender = message["d"]["author"]['id']
            senderNickname = message["d"]['author']['username']
            channel = message['d']['channel_id']
            content = message["d"]["content"]

            self.logger.info("Message Recieved: [Name:{}][UID:{}][CID:{}]: {}".format(senderNickname, sender, channel, content))
        else:
            return None

        if(sender == self.connectorCache['self']['id']):
            return None

        return Message(type, sender, channel, content, senderNickname=senderNickname, timestamp=time.time())

    def __parseLoginData(self, data):
        self.connectorCache['heartbeat_interval'] = data['d']['heartbeat_interval']
        self.connectorCache['session_id'] = data['d']['session_id']
        self.connectorCache['self'] = data['d']['user']
        self.connectorCache['private_channels'] = data['d']['private_channels']
        self.connectorCache['guilds'] = data['d']['guilds']
