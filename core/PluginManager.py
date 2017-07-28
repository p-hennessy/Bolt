"""
    Class Name : PluginManager

    Description:
        Manages loading and unload plugins
            Will bootstrap plugin commands and events when they're loaded

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import sys
import os
import logging
import inspect
import importlib

from core.Plugin import Plugin

class PluginManager():
    def __init__(self, core):
        self.core = core
        self.plugins = {}
        self.logger = logging.getLogger("core.PluginManager")

    def list(self) -> dict:
        return self.plugins


    def status(self, name: str) -> str:
        return self.plugins[name]["status"]

    def load(self, plugin_module: str):
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
            if hasattr(callback, "connector"):
                if not self.core.connection.name == getattr(callback, "connector"):
                    logger.debug("Command \"" + clazz + "." + name + "\" does not meet connector requirements. Skipping registration.")
                    continue

            if hasattr(callback, "is_command"):
                self.core.command.register(
                    getattr(callback, "pattern"),
                    callback,
                    trigger=getattr(callback, "trigger"),
                    access=getattr(callback, "access"),
                    silent=getattr(callback, "silent")
                )

            if hasattr(callback, "is_subscriber"):
                self.core.event.subscribe(getattr(callback, "event"), callback)

            if hasattr(callback, "is_publisher"):
                self.core.event.register(getattr(callback, "event"))

        # Push plugin to our hashtable
        self.plugins[plugin.name] = {"instance":plugin, "module": plugin_module, "status": "Enabled"}
        self.logger.info("Loaded plugin \"" + plugin.name + "\"")

    def unload(self, plugin_name: str):
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
                self.core.command.unregister(commandName)

            if( hasattr(callback, "is_subscriber") ):
                self.core.event.unsubscribe(getattr(callback, "event"), callback)

            if( hasattr(callback, "is_publisher") ):
                self.core.event.unregister(getattr(callback, "event"))

        # Remove from our hashtable
        self.plugins[plugin_name] = {"instance":None, "module":None, "status": "Disabled"}
        self.logger.info("Unloaded plugin \"" + plugin_name + "\"")

    def reload(self, name: str):
        plugin = self.plugins[name]

        if not plugin:
            return

        elif(plugin['status'] == 'Disabled'):
            self.load(name)
        else:
            self.unload(name)
            self.load(name)

    def discover(self, path: str):
          for file in os.listdir(path):
            if not file.startswith('__'):
                if file.endswith(".py"):
                    fullname = os.path.splitext(os.path.basename(file))[0]

                    try:
                        module = importlib.machinery.SourceFileLoader(fullname, os.path.join(path, file)).load_module()
                    except ImportError as e:
                        self.logger.error("{}/{}: {}".format(path, file, e))
                        continue

                    yield module
