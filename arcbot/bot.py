"""
    Description:

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""
import gevent
from gevent import monkey
from gevent import queue

# Patch must happen before requests is imported: https://github.com/requests/requests/issues/3752
gevent.monkey.patch_all()

from arcbot.config import Config
from arcbot.discord.api import API
from arcbot.discord.gateway import Gateway
from arcbot.core.event import EventManager
from arcbot.core.webhook import WebhookManager
from arcbot.core.scheduler import Scheduler

import sys
import logging
import logging.handlers

class Bot():
    def __init__(self, token):
        self.config = Config()
        self._setup_logger()

        self.plugins = []
        self.events = EventManager()
        self.webhooks = WebhookManager()
        self.scheduler = Scheduler()
        self.queue = queue.Queue()

        self.gateway = Gateway(self, token)
        self.api = API(token)


    def run(self):
        self.greenlet_gateway = gevent.spawn(self.gateway.start)
        self.greenlet_scheduler = gevent.spawn(self.scheduler.start)
        self.greenlet_webhooks = gevent.spawn(self.webhooks.start)
        self.greenlet_workers = [gevent.spawn(self.worker) for _ in range(25)]

        greenlets = [
            self.greenlet_gateway,
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

        #Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            "%(created)s %(levelname)s %(name)s.%(funcName)s:%(lineno)s '%(message)s'"
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
        file_handler.setLevel(self.config.log_level)
        log.addHandler(file_handler)

        self.logger = logging.getLogger(__name__)

    def load(self, plugin_module):
        self.plugins.append(plugin_module(self))
