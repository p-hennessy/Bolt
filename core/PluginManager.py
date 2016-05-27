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
import imp
import logging
import inspect

from core.Plugin import Plugin

class PluginManager():
    def __init__(self, core):
        self.core = core
        self.plugins = {}

        self.logger = logging.getLogger("core.PluginManager")
        self.find_plugins()
        sys.path.append("plugins")

    def find_plugins(self):
        """
            Summary:
                Scans through plugin directory looking for potential plugins.
                Appends any plugin it finds to class-level dict

            Args:
                None

            Returns:
                None
        """
        for file in os.listdir("plugins"):
            if not file.startswith('__'):
                if file.endswith(".py"):
                    name = os.path.splitext(file)[0]
                    self.plugins[name] = {"instance": None, "status": "Disabled"}
                else:
                    name = os.path.join('plugins', file, '__init__.py')
                    if os.path.exists(name):
                        self.plugins[file] = {"instance": None, "status": "Disabled"}

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

    def exists(self, name):
        """
            Summary:
                Checks to see if a plugin exists in our bot

            Args:
                name (str): Name used internally for the plugin. Should be the same name as the plugin's class

            Returns:
                (bool): Whether or not a plugin exists
        """
        return name in self.plugins

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

    def load(self, moduleName):
        """
            Summary:
                Loads a plugin,
                registers all commands and events,
                pushes plugin instance to internal hashtable.

            Args:
                moduleName (str): Name of the file that needs to be imported

            Returns:
                None
        """

        try:
            pluginCandidate = imp.find_module(moduleName, path=['plugins'])
            pluginModule = imp.load_module(moduleName, *pluginCandidate)
        except ImportError as e:
            self.logger.error(e)
            return

        plugin = None

        # Find plugin subclass and initialize it
        for name, clazz in inspect.getmembers(pluginModule, inspect.isclass):
            if name == "Plugin":
                continue

            if issubclass(clazz, Plugin):
                plugin = clazz(self.core, name)
                break

        if not plugin:
            self.logger.error("Could not find plugin subclass in module: " + moduleName)
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
        self.plugins[plugin.name] = {"instance":plugin, "module": pluginModule, "status": "Enabled"}
        self.logger.info("Loaded plugin \"" + plugin.name + "\"")

    def unload(self, pluginName):
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
        if(pluginName not in self.plugins):
            self.logger.warning("Unable to unload plugin " + pluginName + ", plugin not loaded")
            return

        # Get plugin object from our hashtable
        plugin = self.plugins[pluginName]["instance"]
        clazz = plugin.__class__.__name__

        if( hasattr(plugin, "deactivate") ):
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
        self.plugins[pluginName] = {"instance":None, "module":None, "status": "Disabled"}
        self.logger.info("Unloaded plugin \"" + pluginName + "\"")

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
