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

from __future__ import print_function
import sys

from core.Watchdog import Watchdog
from core.Command import CommandManager
from core.Event import EventManager
from core.PluginManager import PluginManager
from core.ThreadPool import ThreadPool
from core.Database import Database
from core.ACL import ACL

import threading
from imp import load_module, find_module
from sys import stdout, path, exit
import logging
import logging.handlers
import time

class Bot():

    def __init__(self):
        # Setup logger and load config
        self.setupLogger()
        self.logger.info("Starting new bot session")
        self.logger.info("Loading bot configuration")
        self.config = self.loadConfig("settings")

        # Setup managers
        self.watchdog = Watchdog(self)
        self.plugin = PluginManager(self)
        self.event = EventManager()
        self.command = CommandManager(self)
        self.ACL = ACL()
        self.threadPool = ThreadPool(self.config.threadPoolQueueSize, self.config.threadedWorkers)

        # Setup connection
        self.connection = self.loadConnector(self)

        # Load plugins
        self.logger.info("Loading Plugins")
        self.loadPlugins()

    def login(self):
        self.connection.connect()

    def logout(self):
        self.connection.disconnect()

    def cleanup(self):
        """
            Summary:
                Does any nessessary clean up (like killing threads) before the bot exits

            Args:
                None

            Returns:
                None
        """
        for pluginName in self.config.plugins:
            self.plugin.unload(pluginName)

        self.logout()
        self.threadPool.joinThreads()

    def setupLogger(self):
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
        file_hdlr.setLevel(logging.DEBUG)
        log.addHandler(file_hdlr)

        self.logger = logging.getLogger(__name__)

    def loadConfig(self, configName):
        """
            Summary:
                Establishes a connection to the server
                Emits login event
                Starts message consumer thread
                Expects to have already loaded connection module
                Exits if it cannot find or load the config

            Args:
                configName (str): Name of the config module to be loaded

            Returns:
                (Config): instance of Config class, storing all global config options
        """

        path.append("conf")

        try:
            configCanadiate = find_module(configName)
            configModule = load_module(configName, *configCanadiate)

            config = configModule.Config()
            self.logger.info("Loaded configuration from \"" + configCanadiate[1] + "\"")
            logging.getLogger('').setLevel(config.loglevel)

            return config

        except ImportError as e:
            self.logger.critical("ImportError: " + str(e))
            sys.exit(1)
        except AttributeError as e:
            self.logger.critical("Config class not found in conf/" + configName)
            sys.exit(1)

    def loadConnector(self, core):
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
            connectorCandidate = find_module(self.config.connector)
            connectorModule = load_module(self.config.connector, *connectorCandidate)
            connector = getattr(connectorModule, self.config.connector)(core, **self.config.connectorOptions)
            self.logger.info("Loaded connector from: \"" +  connectorCandidate[1] + "\"")

            return connector

        except ImportError as e:
            self.logger.critical("ImportError: " + str(e))
            exit(1)
        except AttributeError as e:
            print(e)
            self.logger.critical("Could not find connector class: " + self.config.connector)
            exit(1)

    def loadPlugins(self):
        """
            Summary:
                Looks in plugins list in config and attempts to load each

            Args:
                None

            Returns:
                None
        """
        for pluginName in self.config.plugins:
            self.plugin.load(pluginName)
