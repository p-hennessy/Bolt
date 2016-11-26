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

import requests
import base64
import json
import logging
import threading
import time
import websocket

from core.Connector import Connector
from core.Decorators import ttl_cache
from core.Message import *

class Discord(Connector):
    def __init__(self, core, token):
        super(Discord, self).__init__()
        self.core   = core
        self.logger = logging.getLogger(__name__)
        self.name   = __name__

        self.logger.info(self.core.name)

        # Authentication / Connection Data
        self.cache = {
            "heartbeat_interval": 41250,
            "session_id":"",
            "self":{},
            "private_channels":[],
            "guilds":[]
        }

        self.connected = False              # Boolean for handling connection state
        self.token     = token              # Token used to authenticate api requests
        self.socket    = None               # Websocket connection handler to Discord

        self.auth_headers = {"authorization": "Bot " + self.token, "Content-Type": 'application/json'}
        self.api_url = "https://discordapp.com/api/"

        # Internal threads
        self.keep_alive_thread = None
        self.message_consumer_thread = None

        # Events that this connector publishes
        core.event.register('connector.connect')
        core.event.register('connector.member_add')
        core.event.register('connector.member_update')
        core.event.register('connector.member_remove')

        core.event.register('connector.role_create')
        core.event.register('connector.role_update')
        core.event.register('connector.role_delete')

        core.event.register('connector.pressence')
        core.event.register('connector.message')

    def connect(self):
        # Connect to Discord, post login credentials
        self.logger.info("Attempting connection to Discord servers")

        # Request a WebSocket URL
        socket_url = requests.get(self.api_url + "gateway", headers=self.auth_headers).json()["url"]
        self.socket = websocket.create_connection(socket_url)

        # Immediately pass message to server about your connection
        self._write_socket({
            "op": 2,
            "v": 5,
            "d": {
                "token": self.token,
                "properties": {
                    "$os": system(),
                    "$device":"Python"
                },
                "compress": False
            }
        })

        login_data = self._read_socket()
        self.cache['heartbeat_interval'] = login_data['d']['heartbeat_interval']
        self.cache['session_id']         = login_data['d']['session_id']
        self.cache['self']               = login_data['d']['user']
        self.cache['private_channels']   = login_data['d']['private_channels']
        self.cache['guilds']             = login_data['d']['guilds']

        # Set websocket to nonblocking so we can exit a thread reading from the socket if we need to
        self.socket.sock.setblocking(0)
        self.connected = True

        self.logger.info("Succesful login to Discord")
        self.core.event.notify('connect')

        # Create and start threads
        self.keep_alive_thread = threading.Thread(target=self._keep_alive, name="keep_alive_thread")
        self.keep_alive_thread.daemon = True
        self.keep_alive_thread.start()

        self.message_consumer_thread = threading.Thread(target=self._message_consumer, name="message_consumer_thread")
        self.message_consumer_thread.daemon = True
        self.message_consumer_thread.start()

    def disconnect(self):
        self.core.event.notify('disconnect')
        self.connected = False

        # Join threads if they exist
        if isinstance(self.keep_alive_thread, threading.Thread):
            self.keep_alive_thread.join()

        if isinstance(self.message_consumer_thread, threading.Thread):
            self.message_consumer_thread.join()

        self.logger.debug('Joined message_consumer and keep_alive threads')

        # Close websocket if it is established
        if isinstance(self.socket, websocket.WebSocket):
            self.socket.close()

        self.logger.info("Disconnected from Discord")

    def say(self, channel, message, embed={}, mentions=[]):
        self.logger.debug("Sending message to channel " + channel)

        for user in mentions:
            message = "<@{}> ".format(user) + message

        endpoint = self.api_url + "channels/{}/messages".format(channel)
        data = {
            "content": "{}".format(message),
            "embed": embed,
            "mentions": mentions
        }

        try:
            response = requests.post(endpoint, data=json.dumps(data), headers=self.auth_headers)
            response.raise_for_status()
        except Exception as e:
            self.logger.warning('Send message to channel \'{}\' failed: {}'.format(channel, e))
            print(response.text)

    def reply(self, user, channel, message):
        self.say(channel, message, mentions=[user])

    def whisper(self, user, message):
        channel = self.get_private_channel(user)
        self.say(channel, message)

    def upload(self, channel, file):
        self.logger.debug('Uploading file to channel ' + channel)

        endpoint = self.api_url + "channels/{}/messages".format(channel)
        files = {'file': open(file, 'rb')}

        try:
            response = requests.post(endpoint,  files=files, headers=self.auth_headers)
            response.raise_for_status()
        except Exception as e:
            self.logger.warning('Upload of {} to channel {} failed'.format(file, channel))

    def embed(self, channel, embed):
        self.say(channel, "", embed)

    # Discord Specific
    def get_user(self, id):
        user = requests.get(self.api_url + "users/{}".format(userID), headers=self.auth_headers).json()
        return user

    def leave_guild(self, guild_id):
        requests.delete(self.api_url + "users/@me/guilds/{}".format(guild_id), headers={"authorization": self.token})

    def get_servers(self):
        endpoint = self.api_url + "users/@me/guilds"

        try:
            response = requests.get(endpoint, headers=self.auth_headers)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            self.logger.warning('{}'.format(e))

    def get_private_channel(self, user):
        for channel in self.cache['private_channels']:
            if channel['recipient']['id'] == user:
                return channel['id']
        else:
            response = requests.post(self.api_url + "users/@me/channels", data={"recipient_id": "{}".format(user)}, headers=self.auth_headers)
            channel = reponse.json()

            self.cache['private_channels'].append(channel)
            return channel['id']

    def set_status(self, status):
        self._write_socket({
            "op":3,
            "d":{
                "idle_since":None,
                "game": {
                    "name": status
                }
            }
        })

    def set_avatar(self, image_path):
        with open(image_path, "rb") as avatar_image:
            raw_image = avatar_image.read()

        raw = base64.b64encode(raw_image)
        image_data = "data:image/jpeg;base64," + raw.decode('ascii')

        response = requests.patch(self.api_url + "users/@me", data={"avatar": image_data}, headers=self.auth_headers)

    # Thread Methods
    def _keep_alive(self):
        self.logger.debug("Spawning keep_alive thread at interval: " + str(self.cache['heartbeat_interval']))

        last_heartbeat = time.time()
        heartbeat_interval = self.cache['heartbeat_interval'] / 1000

        while self.connected:
            now = time.time()

            if (now - last_heartbeat) >= heartbeat_interval - 1:
                self._write_socket({"op":1,"d": time.time()})
                self.logger.debug("Keep Alive")

                last_heartbeat = time.time()

            time.sleep(1)

    def _message_consumer(self):
        self.logger.debug("Spawning message_consumer thread")

        while self.connected:
            # Sleep is good for the body; also so we don't hog the CPU polling the socket
            time.sleep(0.1)

            # Read data off of socket
            raw_message = self._read_socket()
            if not raw_message:
                continue

            # Parse raw message
            message = self._parse_message(raw_message)
            if not message:
                continue

            # Have worker thread take it from here
            self.core.workers.queue(self._handleMessage, message)

    # Handler Methods
    def _handleMessage(self, message):
        # If incoming message is a MESSAGE text
        if message.type == messageType.MESSAGE:
            self.core.event.notify("message",  message=message)
            self.core.command.check(message)

        # If incoming message is PRESSENCE update
        elif type == messageType.PRESSENCE:
            self.core.event.notify("pressence", message=message)

    # Socket Methods
    def _write_socket(self, data):
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
            if not self.connected:
                return
            self.logger.warning("Websocket unexpectedly closed.")
            self.connected = False

    def _read_socket(self):
        data = ""
        while True:
            try:
                data += self.socket.recv()

                if data:
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
                if not self.connected:
                    return
                self.logger.warning("Websocket unexpectedly closed.")
                self.connected = False

    # Parser Methods
    def _parse_message(self, message):
        type = content = sender = sender_name = channel = content = timestamp = None

        if message["t"] == "MESSAGE_CREATE":
            type = messageType.MESSAGE
            sender = message["d"]["author"]['id']
            sender_name = message["d"]['author']['username']
            channel = message['d']['channel_id']
            content = message["d"]["content"]
        else:
            pass

        if sender == self.cache['self']['id']:
            return None

        return Message(type, sender, channel, content=content, sender_name=sender_name, timestamp=time.time())
