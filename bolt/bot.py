# flake8: noqa: E402
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

from bolt.discord.api import API
from bolt.discord.websocket import Websocket
from bolt.core.event import EventManager
from bolt.core.webhook import WebhookServer
from bolt.core.scheduler import Scheduler
from bolt.core.plugin import Plugin
from bolt.core.config import Config
from bolt.utils import setup_logger

from pymongo import MongoClient

import os
import logging
import logging.handlers
import inspect
import importlib.util


class Bot():
    VERSION = "0.4.3"

    def __init__(self, config_path):
        self.config = Config(config_path)
        setup_logger(self.config)
        self.logger = logging.getLogger(__name__)

        # Core
        self.plugins = []
        self.events = EventManager()
        self.webhooks = WebhookServer()
        self.scheduler = Scheduler(self)
        self.queue = queue.Queue()

        # Backend
        self.websocket = Websocket(self, self.config.api_key)
        self.api = API(self.config.api_key)

        # Database
        self.database_client = MongoClient()
        user_database = self.database_client[f"core-users"]
        self.users = user_database.users

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

    def load_plugin(self, path):
        name = path.split('/')[-1].split('.')[0]
        path = os.path.abspath(path)
        self.logger.info(f"Loading plugin \"{name}\" from \"{path}\"")

        plugin_module_spec = importlib.util.spec_from_file_location(name, path)
        plugin_module = importlib.util.module_from_spec(plugin_module_spec)
        plugin_module_spec.loader.exec_module(plugin_module)

        for name, clazz in inspect.getmembers(plugin_module, inspect.isclass):
            if issubclass(clazz, Plugin) and name != "Plugin":
                new_plugin = clazz(self)
                new_plugin.activate()

                self.plugins.append(new_plugin)
                break

    def unload_plugin(self, name):
        found_index = None
        for index, plugin in self.plugins.enumerate():
            if plugin.name == name:
                found_index = index
                break
        else:
            return

        plugin = self.plugins.pop(found_index)
        plugin.deactivate()
