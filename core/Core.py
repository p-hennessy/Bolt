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

import conf.settings as config

from core.ACL import ACL
from core.Command import CommandManager
from core.Database import Database
from core.Event import EventManager
from core.PluginManager import PluginManager
from core.Workers import Workers
from core.Watchdog import Watchdog

from imp import load_module, find_module
from sys import stdout, path, exit
import logging
import logging.handlers
import time

class Bot():
    def __init__(self):
        # Setup logger and load config
        self.setup_logger()
        self.config = self.load_config("settings")

        # Setup managers
        self.watchdog = Watchdog(self)
        self.plugin = PluginManager(self)
        self.event = EventManager(self)
        self.command = CommandManager(self)
        self.ACL = ACL()
        self.workers = Workers(self.config.worker_queue_size, self.config.worker_threads)

        # Setup connection
        self.connection = self.load_connector(self)

        # Load plugins
        self.logger.info("Loading Plugins")
        self.load_plugins()


    def login(self):
        self.connection.connect()

    def logout(self):
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

        # Create console handler
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

        self.logger = logging.getLogger(__name__)

    def load_config(self, name):
        """
            Summary:
                Establishes a connection to the server
                Emits login event
                Starts message consumer thread
                Expects to have already loaded connection module
                Exits if it cannot find or load the config

            Args:
                name (str): Name of the config module to be loaded

            Returns:
                (Config): instance of Config class, storing all global config options
        """

        path.append("conf")

        try:
            config_canadiate = find_module(name, path=['conf'])
            config_module = load_module(name, *config_canadiate)

            self.logger.info("Loaded configuration from \"" + config_canadiate[1] + "\"")
            logging.getLogger('').setLevel(config_module.log_level)

            return config_module

        except ImportError as e:
            self.logger.critical("ImportError: " + str(e))
            exit(1)
        except AttributeError as e:
            self.logger.critical("Config class not found in conf/" + name)
            exit(1)

    def load_connector(self, core):
        """
            Summary:
                Looks for and loads the connector defined in config
                Will exit if cannot find or load the connector module

            Args:
                None

            Returns:
                (Connector): The low level connection manager instance
        """
        path.append("connectors")

        try:
            connector_candidate = find_module(config.connector, path=["connectors"])
            connector_module = load_module(config.connector, *connector_candidate)
            connector = getattr(connector_module, config.connector)(core, **config.connector_options)
            self.logger.info("Loaded connector from: \"" +  connector_candidate[1] + "\"")

            return connector

        except ImportError as e:
            self.logger.critical("ImportError: " + str(e))
            exit(1)
        except AttributeError as e:
            print(e)
            self.logger.critical("Could not find connector class: " + config.connector)
            exit(1)

    def load_plugins(self):
        """
            Summary:
                Looks in plugins list in config and attempts to load each

            Args:
                None

            Returns:
                None
        """
        for plugin in config.plugins:
            self.plugin.load(plugin)
