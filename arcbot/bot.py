"""
    Description:
        Main entry point for the bot to function
        Composes multiple things to allow for an interface to plugins

    Contributors:
        - Patrick Hennessy
"""
import gevent
from gevent import monkey
from gevent import queue

# Patch must happen before requests is imported:
# https://github.com/requests/requests/issues/3752
monkey.patch_all()

from arcbot.discord.api import API
from arcbot.discord.websocket import Websocket
from arcbot.core.event import EventManager
from arcbot.core.webhook import WebhookServer
from arcbot.core.scheduler import Scheduler
from arcbot.core.plugin import Plugin

from pymongo import MongoClient

import sys
import logging
import logging.handlers
import inspect


class Bot():
    def __init__(self, token):
        self._setup_logger()

        # Core
        self.plugins = []
        self.events = EventManager()
        self.webhooks = WebhookServer()
        self.scheduler = Scheduler(self)
        self.queue = queue.Queue()

        # Backend
        self.websocket = Websocket(self, token)
        self.api = API(token)

        # Database
        self.database_client = MongoClient()

    def run(self):
        self.greenlet_websocket = gevent.spawn(self.websocket.start)
        self.greenlet_scheduler = gevent.spawn(self.scheduler.start)
        self.greenlet_webhooks = gevent.spawn(self.webhooks.start)
        self.greenlet_workers = [gevent.spawn(self.worker) for _ in range(25)]

        greenlets = [
            self.greenlet_websocket,
            self.greenlet_scheduler,
            self.greenlet_webhooks,
        ]
        greenlets.extend(self.greenlet_workers)
        gevent.joinall(greenlets)

    def worker(self):
        while True:
            callback, args, kwargs = self.queue.get()

            try:
                callback(*args, **kwargs)
            except Exception as e:
                self.logger.warning(f"Exception running task: {callback}: {e}")
            finally:
                gevent.sleep(0)

    def _setup_logger(self):
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

        log = logging.getLogger('')
        log.setLevel(logging.DEBUG)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            "%(levelname)s %(name)s.%(funcName)s:%(lineno)s '%(message)s'"
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.DEBUG)
        log.addHandler(console_handler)

        # Create log file handler
        file_handler = logging.handlers.TimedRotatingFileHandler("logs/botlog.json", when="midnight")
        file_formatter = logging.Formatter(
            '{{"time":"{created}","lvl":"{levelname}","src":"{name}.{funcName}:{lineno}","msg":"{message}"}}',
            datefmt='%m/%d/%Y %H:%M:%S',
            style="{"
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)
        log.addHandler(file_handler)

        self.logger = logging.getLogger(__name__)

    def load(self, plugin_module):
        for name, clazz in inspect.getmembers(plugin_module, inspect.isclass):
            if issubclass(clazz, Plugin) and name != "Plugin":
                new_plugin = clazz(self)
                new_plugin.activate()

                self.plugins.append(new_plugin)
                break
