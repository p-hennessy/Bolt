"""
    Description:
        Provides functionality for connecting to Discord chat server

    Contributors:
        - Patrick Hennessy
"""
from bolt.discord.events import Subscription
from bolt.discord.events import EventHandler
from bolt.discord import events

from bolt.discord.cache import Cache
from bolt.utils import snakecase_to_camelcase
from bolt.core.exceptions import InvalidBotToken

from datetime import timedelta
from platform import system
from enum import IntEnum
import ujson as json
import websocket
import logging
import gevent
import time


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
        self.login_time = 0
        self.heartbeat_greenlet = None

        self.cache = Cache(self.bot.api)
        self.event_handler = EventHandler(self.bot)

        # Subscribe to events
        self.subscriptions = [
            Subscription("Ready", self.handle_gateway_ready),
            Subscription("MessageCreate", self.handle_gateway_message)
        ]

    def start(self):
        self.logger.debug('Spawning Gateway Greenlet')

        gateway = self.bot.api.get_gateway_bot()
        if gateway.get("message") == "401: Unauthorized":
            raise InvalidBotToken()

        self.socket_url = f"{gateway['url']}?v=6&encoding=json"
        self.login_time = time.time()

        self.websocket_app = websocket.WebSocketApp(
            self.socket_url,
            on_message=self.handle_websocket_message,
            on_error=self.handle_websocket_error,
            on_open=self.handle_websocket_open,
            on_close=self.handle_websocket_close
        )
        self.logger.info("Successfully connected to Discord")
        self.websocket_app.run_forever()

    def send(self, data):
        self.websocket.send(json.dumps(data))

    def heartbeat(self, interval):
        while True:
            self._heartbeat_start = time.monotonic()
            self.logger.debug(f'Heartbeat. Ping: {self.ping} @ {int(self._heartbeat_start)}')
            self.send({"op": GatewayOpCodes.HEARTBEAT, "d": self.sequence})
            gevent.sleep(interval / 1000)

    def handle_websocket_error(self, socket, error):
        self.logger.warning(f"Socket error {error}")

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
        op_code = message.get('op', None)

        if op_code == GatewayOpCodes.DISPATCH:
            event_name = snakecase_to_camelcase(message['t'])
            event_class = getattr(events, event_name)

            event = event_class.marshal(message)
            event.remarshal(message['d'])
            event.cache = self.cache

            self.sequence = event.sequence

            # Update cache
            self.event_handler.dispatch(event, self.cache.subscriptions)

            # Dispatch event to all subscribers
            self.event_handler.dispatch(event, self.subscriptions)
            for plugin in self.bot.plugins:
                if plugin.enabled is True:
                    self.event_handler.dispatch(event, plugin.subscriptions, queue=True)

        elif op_code == GatewayOpCodes.RECONNECT:
            self.logger.warning("Got reconnect signal")
            self.websocket.close()

        elif op_code == GatewayOpCodes.INVALID_SESSION:
            self.logger.warning("Invalid websocket session")
            self.websocket.close()

        elif op_code == GatewayOpCodes.HELLO:
            self.send({
                "op": GatewayOpCodes.IDENTIFY,
                "v": 6,
                "d": {
                    "token": self.token,
                    "shard": [
                        self.bot.config.shard_id,
                        self.bot.config.shard_total
                    ],
                    "properties": {
                        "$os": system(),
                        "$browser": "Bolt",
                        "$device": "Bolt"
                    },
                    "large_threshold": 50,
                    "compress": False
                }
            })

            self.heartbeat_greenlet = gevent.spawn(self.heartbeat, message['d']['heartbeat_interval'])

        elif op_code == GatewayOpCodes.HEARTBEAT_ACK:
            delta = timedelta(seconds=time.monotonic()-self._heartbeat_start)
            self.ping = round(delta.microseconds / 1000)

        else:
            self.logger.error(f"Recieved unexpected OP code: {op_code}")

        return True

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
        if event.message.author.id == self.cache.user.id:
            return

        content = event.message.content
        for command in self.iter_commands():
            if command.matches(content):
                event.arguments = command.parse(content)

                for hook in self.iter_pre_command_hooks():
                    output = hook(command, event)
                    if output is False:
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


class GatewayOpCodes(IntEnum):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    STATUS_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11
