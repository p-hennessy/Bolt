"""
    Description:
        Provides functionality for connecting to Discord chat server

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it under the terms of the GNU
        General Public License v3; as published by the Free Software Foundation
"""
from arcbot.core.event import Event
from arcbot.discord.api import API
from arcbot.discord.events import Events

from datetime import timedelta
from platform import system
import ujson as json
import websocket
import logging
import gevent
import time
import re

class Gateway():
    def __init__(self, bot, token):
        self.bot = bot
        self.token = token
        self.api = API(self.token)
        self.logger = logging.getLogger(__name__)

        self.websocket = None
        self.ping = -1
        self.sequence = 0
        self.id = None
        self.login_time = 0

        # Subscribe to events
        self.bot.events.subscribe(Events.MESSAGE_CREATE, self.handle_gateway_message)

    def start(self):
        self.logger.debug('Spawning Gateway Greenlet')
        self.socket_url = f"{self.api.get_gateway_bot()['url']}?v=6&encoding=json"

        self.websocket_app = websocket.WebSocketApp(
            self.socket_url,
            on_message=self.handle_websocket_message,
            on_error=self.handle_websocket_error,
            on_open=self.handle_websocket_open,
            on_close=self.handle_websocket_close
        )
        self.websocket_app.run_forever()

    def send(self, data):
        self.websocket.send(json.dumps(data))

    def heartbeat(self, interval):
        while True:
            self.logger.debug(f'Heartbeat. Ping: {self.ping}')
            self._heartbeat_start = time.monotonic()
            self.send({"op":1,"d": self.sequence})
            gevent.sleep(interval / 1000)

    def handle_websocket_error(self, socket, error):
        print(error)

    def handle_websocket_close(self, socket):
        self.websocket = None

    def handle_websocket_open(self, socket):
        self.login_time = time.time()
        self.websocket = socket

    def handle_websocket_message(self, socket, message):
        message = json.loads(message)
        op_code = message['op']

        # Dispatch Event
        if op_code == 0:
            self.sequence = message['s']
            event_id = getattr(Events, message['t'])
            event = Event.from_message(message)

            for callback in self.bot.events.subscriptions.get(event_id, []):
                self.bot.queue.put((callback, [event], {}))

        # Reconnect
        elif op_code == 7:
            self.websocket.close()

        # Invalid Session
        elif op_code == 9:
            self.websocket.close()

        # Hello
        elif op_code == 10:
            self.send({
                "op": 2,
                "v": 6,
                "d": {
                    "token": self.token,
                    "properties": {
                        "$os": system(),
                        "$browser": "Arcbot",
                        "$device": "Arcbot"
                    },
                    "large_threshold": 50,
                    "compress": False
                }
            })

            gevent.spawn(self.heartbeat, message['d']['heartbeat_interval'])

        # Heartbeak ACK
        elif op_code == 11:
            delta = timedelta(seconds=time.monotonic()-self._heartbeat_start)
            self.ping = round(delta.microseconds / 1000)

    @property
    def status(self):
        if not self._status:
            self._status = None

        return self._status

    @status.setter
    def status(self, status):
        self._status = status
        self.send({
            "op":3,
            "d":{
                "idle_since": None,
                "game": {
                    "name": status
                },
                "afk": False
            }
        })
        gevent.sleep(0)

    # Event handlers
    def handle_gateway_message(self, event):
        for plugin in self.bot.plugins:
            if not plugin.enabled:
                continue

            for command in plugin.commands:
                if event.content.startswith(command.trigger):
                    content = event.content.replace(command.trigger, "", 1)
                    match = re.search(command.pattern, content)

                    if match:
                        setattr(event, "arguments", match)
                        self.bot.queue.put((command.invoke, [event], {}))
                        gevent.sleep(0)
