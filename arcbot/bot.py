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

# Patch must happen before requests is imported: https://github.com/requests/requests/issues/3752
gevent.monkey.patch_all()

from arcbot.config import Config
from arcbot.discord.api import API
from arcbot.discord.gateway import Gateway
from arcbot.core.plugin import PluginManager
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

        self.events = EventManager()
        self.plugins = PluginManager(self)
        self.webhooks = WebhookManager()
        self.scheduler = Scheduler()

        self.gateway = Gateway(self, token)
        self.api = API(token)

    def run(self):
        greenlets = [
            gevent.spawn(self.gateway.start),
            gevent.spawn(self.scheduler.start),
            gevent.spawn(self.webhooks.start)
        ]
        monkey.patch_all()
        gevent.joinall(greenlets)

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

    def load(self, module):
        self.plugins.load(module)
