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

from arcbot.ACL import ACL
from arcbot.Command import CommandManager
from arcbot.PluginManager import PluginManager
from arcbot.ThreadPool import ThreadPool
from arcbot.Discord import event
import arcbot.Discord as discord

import importlib
import os
import time

from colorlog import ColoredFormatter
from sys import stdout
import logging
import logging.handlers

class Bot():
    name = "Arcbot"
    trigger = "arcbot "
    avatar = None
    log_level = logging.DEBUG

    worker_threads = 12
    worker_queue_size = 100

    connection_retry = 3
    connection_timeout = 300

    def __init__(self, token):
        self.setup_logger()

        self.connection = discord.Discord(self, token)
        self.event = event
        self.workers = ThreadPool(self.worker_queue_size, self.worker_threads)
        self.plugin = PluginManager(self)
        self.command = CommandManager(self)
        self.ACL = ACL()


    def connect(self) -> None:
        self.connection.connect()

    def disconnect(self) -> None:
        self.connection.disconnect()

    def exit(self) -> None:
        self.workers.threads = 0

    def setup_logger(self) -> None:
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
        logging.getLogger('peewee').setLevel(logging.WARNING)

        log = logging.getLogger('')
        log.setLevel(self.log_level)

        #Create console handler
        console_handler = logging.StreamHandler(stdout)
        console_formatter = ColoredFormatter(
            "%(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)-25.25s%(reset)s %(white)s%(message)s%(reset)s",
            datefmt="[%m/%d/%Y %H:%M:%S]",
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bg_red',
            }
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(self.log_level)
        log.addHandler(console_handler)

        # Create log file handler
        file_handler = logging.handlers.TimedRotatingFileHandler("logs/botlog.json", when="midnight")
        file_formatter = logging.Formatter(
            '{{"time":"{asctime}","lvl":"{levelname}","src":"{name}","msg":"{message}"}}',
            datefmt='%m/%d/%Y %H:%M:%S',
            style="{"
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(self.log_level)
        log.addHandler(file_handler)

        self.logger = logging.getLogger(__name__)

    def load_module(self, path: str) -> None:
        try:
            fullname = os.path.splitext(os.path.basename(path))[0]
            module = importlib.machinery.SourceFileLoader(fullname, path).load_module()

            return module
        except ImportError as e:
            self.logger.critical("ImportError: " + str(e))

    def run_forever(self):
        while True:
            time.sleep(1)

            if not self.connection.connected:
                self.logger.warning("Connection is closed, attempting reconnection")

                for retry in range(0, self.connection_retry):
                    if self.connection.connected:
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
