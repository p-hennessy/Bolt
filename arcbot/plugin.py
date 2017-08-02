"""
    Class Name : Plugin

    Description:
        Superclass for which all plugins are derived

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import logging
import sys
import os
import logging
import inspect
import importlib

class Plugin(object):
    def __init__(self, bot, name):
        self.bot = bot
        self.name = name

        self.api = self.bot.backend.api
        self.say = self.bot.backend.say
        self.whisper = self.bot.backend.whisper
        self.upload = self.bot.backend.upload

        self.logger = logging.getLogger(f"plugins.{self.name}")

    def activate(self):
        pass

    def deactivate(self):
        pass

class PluginManager():
    def __init__(self, core):
        self.core = core
        self.plugins = {}
        self.logger = logging.getLogger(__name__)

    def list(self):
        return self.plugins


    def status(self, name):
        return self.plugins[name]["status"]

    def load(self, plugin_module):
        # Find plugin subclass and initialize it
        plugin = None

        for name, clazz in inspect.getmembers(plugin_module, inspect.isclass):
            if name == "Plugin":
                continue

            if issubclass(clazz, Plugin):
                plugin = clazz(self.core, name)
                break

        if not plugin:
            self.logger.error("Could not find plugin subclass in module: " + plugin_module)
            return

        # Call activate() if it exists
        if hasattr(plugin, "activate"):
            plugin.activate()

        # Register plugin commands and events
        for name, callback in inspect.getmembers(plugin, inspect.ismethod):
            if hasattr(callback, "is_command"):
                self.core.commands.register(
                    getattr(callback, "pattern"),
                    callback,
                    trigger=getattr(callback, "trigger"),
                    access=getattr(callback, "access"),
                    silent=getattr(callback, "silent")
                )

            if hasattr(callback, "is_subscriber"):
                self.core.events.subscribe(getattr(callback, "event"), callback)

        # Push plugin to our hashtable
        self.plugins[plugin.name] = {"instance":plugin, "module": plugin_module, "status": "Enabled"}
        self.logger.info("Loaded plugin \"" + plugin.name + "\"")

    def unload(self, plugin_name):
        # Check if we are managing that plugin
        if(plugin_name not in self.plugins):
            self.logger.warning("Unable to unload plugin " + plugin_name + ", plugin not loaded")
            return

        # Get plugin object from our hashtable
        plugin = self.plugins[plugin_name]["instance"]
        clazz = plugin.__class__.__name__

        if hasattr(plugin, "deactivate"):
            plugin.deactivate()

        # Unregister plugin commands and events
        for name, callback in inspect.getmembers(plugin, inspect.ismethod):
            if( hasattr(callback, "is_command") ):
                commandName = clazz + "." + callback.__name__
                self.core.commands.unregister(commandName)

            if( hasattr(callback, "is_subscriber") ):
                self.core.events.unsubscribe(getattr(callback, "event"), callback)

            if( hasattr(callback, "is_publisher") ):
                self.core.events.unregister(getattr(callback, "event"))

        # Remove from our hashtable
        self.plugins[plugin_name] = {"instance":None, "module":None, "status": "Disabled"}
        self.logger.info("Unloaded plugin \"" + plugin_name + "\"")

    def reload(self, name):
        plugin = self.plugins[name]

        if not plugin:
            return

        elif(plugin['status'] == 'Disabled'):
            self.load(name)
        else:
            self.unload(name)
            self.load(name)
