# flake8: noqa: E402
"""
    Description:
        Main entry point for the bot to function
        Composes multiple things to allow for an interface to plugins

    Contributors:
        - Patrick Hennessy
"""
import gevent
from gevent import monkey, queue
monkey.patch_all()
from gevent.backdoor import BackdoorServer

from bolt.discord.api import API
from bolt.discord.websocket import Websocket
from bolt.core.webhook import WebhookServer
from bolt.core.scheduler import Scheduler
from bolt.core.config import Config
from bolt.core.loader import Loader
from bolt.utils import setup_logger

from pymongo import MongoClient

import logging


class Bot():
    VERSION = "0.8.0"

    def __init__(self, config_path):

        self.config = Config.from_yaml_file(config_path)
        setup_logger(self.config)
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"Initializing Bolt v{self.VERSION}...")

        # Core
        self.plugins = []
        self.webhooks = WebhookServer(self)
        self.scheduler = Scheduler(self)
        self.queue = queue.Queue()
        self.loader = Loader(self)

        # Backend
        self.api = API(self.config.api_key)
        self.websocket = Websocket(self, self.config.api_key)

        # Database
        self.database_client = MongoClient(ssl=self.config.mongo_database_use_tls)
        user_database = self.database_client[f"core-users"]
        self.users = user_database.users

    def run(self):
        self.logger.debug('Starting main event loop')
        greenlets = []

        # Websocket Thread
        self.greenlet_websocket = gevent.spawn(self.websocket.start)
        greenlets.append(self.greenlet_websocket)

        # Scheduler Thread
        self.greenlet_scheduler = gevent.spawn(self.scheduler.start)
        greenlets.append(self.greenlet_scheduler)

        # Thread Spawner
        self.greenlet_threadspawner = gevent.spawn(self.thread_spawner)
        greenlets.append(self.greenlet_threadspawner)

        # Worker Thread(s) - Configurable
        self.greenlet_workers = [gevent.spawn(self.worker) for _ in range(self.config.worker_threads)]
        greenlets.extend(self.greenlet_workers)

        # Backdoor Server thread - Configurable
        if self.config.backdoor_enable is True:
            self.greenlet_backdoor = gevent.spawn(self.backdoor)
            greenlets.append(self.greenlet_backdoor)

        # Webhook Thread - Configurable
        if self.config.webhook_enable is True:
            self.greenlet_webhooks = gevent.spawn(self.webhooks.start)
            greenlets.append(self.greenlet_webhooks)

        gevent.joinall(greenlets)

    def thread_spawner(self):
        while True:
            for plugin in self.plugins:
                if plugin.enabled is False:
                    continue

                while True:
                    try:
                        callback = plugin.greenlet_queue.get_nowait()
                        self.logger.debug(f"Spawning greenlet for {callback}")
                        plugin.greenlets.append(gevent.spawn(callback))
                    except queue.Empty:
                        break

            gevent.sleep(1)

    def backdoor(self):
        self.logger.debug('Spawning Backdoor Greenlet')
        self.logger.warning("The backdoor server should be used for dev purposes only!")

        if self.config.backdoor_host == "0.0.0.0":
            self.logger.warning("Backdoor server should never bind to 0.0.0.0! This is extremely dangerous!")

        server = BackdoorServer((self.config.backdoor_host, self.config.backdoor_port), locals={'bot': self})
        server.serve_forever()

    def worker(self):
        while True:
            callback, args, kwargs = self.queue.get()

            try:
                callback(*args, **kwargs)
            except gevent.GreenletExit:
                self.logger.debug("Recieved kill signal from main thread. Exiting")
                break
            except Exception as e:
                module_name = f"{callback.__self__.__module__}"
                class_name = f"{callback.__self__.__class__.__name__}"
                method_name = f"{callback.__name__}"

                self.logger.warning(f"Exception \"{type(e).__name__}\" raised in task: {module_name}.{class_name}.{method_name}: {e}", exc_info=True)
            finally:
                gevent.sleep(0)
