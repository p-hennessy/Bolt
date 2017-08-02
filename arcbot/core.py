"""
    Class Name : Core

    Description:
        Provides an extensible engine for plugins to interact with
        Features:
            - Publish / Subscribe Event System
            - Plugin manager
            - Configuration manager
            - User, Channel and Group Date manager

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from .discord import Discord
from .config import Config
from .plugin import Plugin
from .plugin import PluginManager
from .event import EventManager
from .threadpool import ThreadPool
from .command import CommandManager

import importlib
import os
import time
import sys

import logging
import logging.handlers

class Bot():
    def __init__(self, token):
        self.config = Config()
        self._setup_logger()

        self.thread_pool = ThreadPool(self.config.queue_size, self.config.threads)

        self.events = EventManager()
        self.plugins = PluginManager(self)
        self.commands = CommandManager(self)

        self.backend = Discord(self, token)

    def connect(self):
        self.backend.connect()

    def disconnect(self):
        self.backend.disconnect()

    def exit(self):
        self.thread_pool.threads = 0

    def _setup_logger(self):
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

        log = logging.getLogger('')
        log.setLevel(self.config.log_level)

        #Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)-25.25s %(message)s",
            datefmt="[%m/%d/%Y %H:%M:%S]"
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(self.config.log_level)
        log.addHandler(console_handler)

        # Create log file handler
        file_handler = logging.handlers.TimedRotatingFileHandler("logs/botlog.json", when="midnight")
        file_formatter = logging.Formatter(
            '{{"time":"{asctime}","lvl":"{levelname}","src":"{name}","msg":"{message}"}}',
            datefmt='%m/%d/%Y %H:%M:%S',
            style="{"
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(self.config.log_level)
        log.addHandler(file_handler)

        self.logger = logging.getLogger(__name__)

    def load(self, module):
        self.plugins.load(module)

    def run_forever(self):
        while True:
            time.sleep(1)

            if not self.backend.connected:
                self.logger.warning("Connection is closed, attempting reconnection")

                for retry in range(0, self.connection_retry):
                    if self.backend.connected:
                        break

                    try:
                        self.disconnect()
                        self.connect()
                    except:
                        time.sleep(10)
                        continue

                else:
                    self.logger.warning(f"Failed to reconnect after {self.connection_retry} tries. Sleeping for {self.connection_timeout} seconds.")
                    time.sleep(self.connection_timeout)
