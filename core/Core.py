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

from core.ACL import ACL
from core.Command import CommandManager
from core.Event import EventManager
from core.PluginManager import PluginManager
from core.Workers import Workers
from core.Watchdog import Watchdog
from core.Connector import Connector

import importlib
import imp
import os
import inspect
import logging

from sys import stdout, path, exit
import logging
import logging.handlers
import time

class Bot():
    name = "Arcbot"
    trigger = "arcbot "
    avatar = None
    log_level = logging.DEBUG
    connector = None
    connector_options = {}

    worker_threads = 12
    worker_queue_size = 100
    connection_retry = 3
    connection_timeout = 300

    def __init__(self):
        self.setup_logger()

        # Setup managers
        self.plugin = PluginManager(self)
        self.event = EventManager(self)
        self.command = CommandManager(self)
        self.ACL = ACL()
        self.workers = Workers(self.worker_queue_size, self.worker_threads)

        self.connection = None

        self.event.register("connect")
        self.event.register("disconnect")
        self.event.register("message")
        self.event.register("pressence")


    def connect(self):
        if not self.connection:
            self.connection = self.connector

        self.connection.connect()

    def disconnect(self):
        self.connection.disconnect()

    def exit(self):
        """
            Summary:
                Does any nessessary clean up (like killing threads) before the bot exits

            Args:
                None

            Returns:
                None
        """
        for plugin in config.plugins:
            self.plugin.unload(plugin)

        self.logout()
        self.workers.threads = 0

    def setup_logger(self):
        """
            Summary:
                Creates global settings for all logging
                Pretty colors are pretty

            Args:
                None

            Returns:
                None
        """
        from colorlog import ColoredFormatter
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
        logging.getLogger('peewee').setLevel(logging.WARNING)

        log = logging.getLogger('')
        log.setLevel(logging.INFO)

        #Create console handler
        console_hdlr = logging.StreamHandler(stdout)
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
        console_hdlr.setFormatter(console_formatter)
        console_hdlr.setLevel(logging.INFO)
        log.addHandler(console_hdlr)

        # Create log file handler
        file_hdlr = logging.handlers.TimedRotatingFileHandler("logs/botlog", when="midnight")
        file_formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)-25.25s %(message)s",
            datefmt="[%m/%d/%Y %H:%M:%S]"
        )
        file_hdlr.setFormatter(file_formatter)
        file_hdlr.setLevel(logging.INFO)
        log.addHandler(file_hdlr)

        self.logger = logging.getLogger(self.name + __name__)

    @classmethod
    def discover_plugins(self, path):
          for file in os.listdir(path):
            if not file.startswith('__'):
                if file.endswith(".py"):
                    fullname = os.path.splitext(os.path.basename(file))[0]
                    module = importlib.machinery.SourceFileLoader(fullname, os.path.join(path, file)).load_module()
                    yield module


    def load_module(self, path):
        try:
            fullname = os.path.splitext(os.path.basename(path))[0]
            module = importlib.machinery.SourceFileLoader(fullname, path).load_module()

            return module
        except ImportError as e:
            self.logger.critical("ImportError: " + str(e))
            exit(1)
