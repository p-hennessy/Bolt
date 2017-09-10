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

class Websocket():
    def __init__(self, bot, token):
        self.bot = bot
        self.token = token
        self.logger = logging.getLogger(__name__)

        # Initalize Things
        self.websocket = None
        self.ping = -1
        self.sequence = 0
        self.user_id = None
        self.session_id = None
        self.session_time = 0
        self.login_time = 1503273600
        self.heartbeat_greenlet = None

        # Subscribe to events
        self.bot.events.subscribe(Events.MESSAGE_CREATE, self.handle_gateway_message)
        self.bot.events.subscribe(Events.READY, self.handle_gateway_ready)


    def start(self):
        self.logger.debug('Spawning Gateway Greenlet')
        self.socket_url = f"{self.bot.api.get_gateway_bot()['url']}?v=6&encoding=json"

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
            self._heartbeat_start = time.monotonic()
            self.logger.debug(f'Heartbeat. Ping: {self.ping} @ {self._heartbeat_start}')
            self.send({"op":1,"d": self.sequence})
            gevent.sleep(interval / 1000)

    def handle_websocket_error(self, socket, error):
        self.logger.warning(f"Socket error {error}")
        print(error)

    def handle_websocket_close(self, socket):
        self.logger.warning("Socket closed unexpectedly")

        self.websocket.close()
        self.websocket = None

        if self.heartbeat_greenlet:
            self.heartbeat_greenlet.kill()

        self.start()

    def handle_websocket_open(self, socket):
        self.session_time = time.time()
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
            self.logger.warning("got reconnect sig")
            self.websocket.close()

        # Invalid Session
        elif op_code == 9:
            self.logger.warning("invalid session")
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

            self.heartbeat_greenlet = gevent.spawn(self.heartbeat, message['d']['heartbeat_interval'])

        # Heartbeak ACK
        elif op_code == 11:
            delta = timedelta(seconds=time.monotonic()-self._heartbeat_start)
            self.ping = round(delta.microseconds / 1000)

        else:
            self.logger.error(f"Recived unexpect OP code: {op_code}")


    @property
    def status(self):
        if not self._status:
            self._status = None

        return self._status

    @status.setter
    def status(self, status):
        if not self.websocket:
            return

        self._status = status
        self.send({
            "op": 3,
            "d": {
                "since": None,
                "game": {
                    "name": str(status),
                    "type": 0
                },
                "status": "online",
                "afk": False
            }
        })
        self.logger.debug(f"Setting status: {status}")

    # Event handlers
    def handle_gateway_message(self, event):
        for command in self.iter_commands():
            if event.content.startswith(command.trigger):
                content = event.content.replace(command.trigger, "", 1)
                match = re.search(command.pattern, content)

                if not match:
                    continue

                event.arguments = match

                for hook in self.iter_pre_command_hooks():
                    output = hook(command, event)
                    if output == False:
                        return

                self.bot.queue.put((command.invoke, [event], {}))
                gevent.sleep(0)

    def handle_gateway_ready(self, event):
        self.user_id = event.user.id
        self.session_id = event.session_id

    def iter_commands(self):
        for plugin in self.bot.plugins:
            if not plugin.enabled:
                continue

            for command in plugin.commands:
                yield command

    def iter_pre_command_hooks(self):
        for plugin in self.bot.plugins:
            if not plugin.enabled:
                continue

            for hook in plugin.pre_command_hooks:
                yield hook
