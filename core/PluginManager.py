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

from core.Plugin import Plugin

class PluginManager():
    def __init__(self, core):
        self.core = core
        self.plugins = {}
        self.logger = logging.getLogger("core.PluginManager")

    def list(self):
        """
            Summary:
                Gets a list of plugin names

            Args:
                None

            Returns:
                (dict): Plugin objects
        """
        return self.plugins

    def status(self, name):
        """
            Summary:
                Gets the status of a plugin

            Args:
                pluginName (str): Name used internally for the plugin. Should be the same name as the plugin's class

            Returns:
                (str): String object indicating the status of the plugin; Enabled, Crashed, or Disabled
        """
        return self.plugins[name]["status"]

    def load(self, plugin_module):
        """
            Summary:
                Loads a plugin,
                registers all commands and events,
                pushes plugin instance to internal hashtable.

            Args:
                module_name (str): Name of the file that needs to be imported

            Returns:
                None
        """
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

    def unload(self, plugin_name):
        """
            Summary:
                Unloads a plugin,
                unregisters all commands and events,
                removes plugin instance from internal hashtable.

            Args:
                pluginName (str): Name of the plugin class instance to be unloaded

            Returns:
                None
        """

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

    def reload(self, name):
        """
            Summary:
                Wrapper for unload + load

            Args:
                name (str): Name of the plugin class instance to be reloaded

            Returns:
                None
        """

        plugin = self.plugins[name]

        if not plugin:
            return

        elif(plugin['status'] == 'Disabled'):
            self.load(name)
        else:
            self.unload(name)
            self.load(name)
