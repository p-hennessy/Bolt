"""
    Class Name : Core

    Description:
        Provides an extensible engine for plugins to interact with
        Features:
            - Publish / Subscribe Event System
            - Plugin manager
            - Configuration manager
            - Slack message parser
            - User, Channel and Group Date manager

    Contributors:
        - Patrick Hennessy

    License:
        CL4M-B0T is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Command import CommandManager
from core.Event import EventManager
from core.MessageConsumer import MessageConsumer
from core.PluginManager import PluginManager

from connectors.discord import DiscordConnection

import threading
import imp
import json
import sys
import logging
import inspect
from colorlog import ColoredFormatter

class Bot():

    def __init__(self):
        self.setupLogger()
        self.logger.info("Loading bot configuration")
        self.config = self.loadConfig("settings")

        self.plugins = PluginManager(self)
        self.event = EventManager()
        self.command = CommandManager(self)

        self.connection = DiscordConnection(**self.config.connectorOptions)

        self.messageConsumerThread = MessageConsumer(self)
        self.messageConsumerThread.daemon = True

        # Initialize core events
        self.event.register("connection.login")
        self.event.register("connection.logout")

        self.plugins.load("Chat")
        self.plugins.unload("Chat")
        #self.login()

    def setupLogger(self):
        logging.getLogger("requests").setLevel(logging.WARNING)

        log = logging.getLogger('')

        console_hdlr = logging.StreamHandler(sys.stdout)
        formatter = ColoredFormatter(
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

        console_hdlr.setFormatter(formatter)
        log.addHandler(console_hdlr)
        log.setLevel(logging.DEBUG)

        self.logger = logging.getLogger(__name__)

    def login(self):
        # Connect to the websocket
        self.connection.connect()

        self.servers = self.connection.getServers()
        self.users = self.connection.getUsers()

        # Notify login event
        self.event.notify("connection.login")

        # Start message consumer thread
        self.messageConsumerThread.start()

        #self.connection.say("96451923229556736", "**CL4M-B0T** login successful.")

    def logout(self):
        # Send stop to message consumer, wait for it to finish it's run.
        self.messageConsumerThread.stop()
        self.messageConsumerThread.join()

        # Send stop to all plugins

        # Disconnect from the websocket
        self.connection.disconnect()

        # Notify logout event
        self.event.notify("connection.logout")

    def loadConfig(self, configName):
        sys.path.append("conf")

        try:
            configCanadiate = imp.find_module(configName)
            configModule = imp.load_module(configName, *configCanadiate)

            config = configModule.Config()
            self.logger.info("Loaded configuration from \"conf." + configName + "\"")
            logging.getLogger('').setLevel(config.loglevel)

            return config

        except ImportError as e:
            self.logger.critical("ImportError: " + str(e))
            sys.exit(1)
        except AttributeError as e:
            self.logger.critical("Config class not found in conf/" + configName)
            sys.exit(1)

    def loadConnector(self):
        pass

    def loadPlugins(self):
        pass
