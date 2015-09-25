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

from platform import system

from core.Connector import Connector
from core.User import User
from core.Message import *
from core.Channel import Channel
from core.Server import Server

log = logging.getLogger(__name__)

class DiscordConnection(Connector):
    def __init__(self, email, password):
        self.email = email
        self.password = password

        self.token = None
        self.api = DiscordAPI()

        self.socketURL = None
        self.socket = None
        self.connected = False

        self.keepAliveThread = None

    def connect(self):
        # Connect to Discord, post login credentials
        log.info("Attempting connection to Discord servers")
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

        self.send(initData)
        loginData = self.recieve()
        self.parseLoginData(loginData)

        # Set websocket to nonblocking
        self.socket.sock.setblocking(0)
        self.connected = True

        self.keepAliveThread = threading.Thread(target=self.keepAlive, name="KeepAliveThread")
        self.keepAliveThread.daemon = True
        self.keepAliveThread.start()

    def disconnect(self):
        self.connected = False
        self.socket.close()

    def whisper(self):
        pass

    def keepAlive(self):
        startTime = time.time()

        while self.connected:
            now = time.time()

            if(now - startTime >= ((self.heartbeatInterval / 1000) - 1)):
                self.send({"op":1,"d": now})
                startTime = now

    def say(self, channelID, message):
        self.api.channels.send(self.token, channelID, message)

    def send(self, data):
        self.socket.send(json.dumps(data))

    def recieve(self):
        data = ""
        while True:
            try:
                data += self.socket.recv()

                if(data):
                    return self.parseMessageData(json.loads(data.rstrip()))
                else:
                    return None

            except ValueError as e:
                # Raised when it
                continue

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
        if(message["t"] == "PRESENCE_UPDATE"):
            return Message.pressence(
                message["d"]["status"],
                message["d"]["id"],
            )
        elif(message["t"] == "TYPING_START"):
            return Message.pressence(
                "TYPING",
                message["d"]["user_id"],
            )
        elif(message["t"] == "MESSAGE_CREATE"):
            return Message.text(
                message["d"]["author"]["id"],
                message["d"]["channel_id"],
                message["d"]["content"],
                message["d"]["timestamp"]
            )
        else:
            return message

    def ping(self):
        pass

    def getUsers(self, serverID=None):
        if(self.users):
            returnUsers = self.users
            del self.users
            return returnUsers
        else:
            pass

    def getServers(self):
        if(self.servers):
            returnServers = self.servers
            del self.servers
            return returnServers

    def getUser(self, userID):
        pass

    def getChannels(self, serverID):
        pass

    def getChannel(self, serverID, channelID):
        pass

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

    def send(self, token, channelID, content):
        return self.request("POST", "channels/" + channelID + "/messages", postData={"content": content, "nonce": random.getrandbits(64), "mentions":[]}, token=token)

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
