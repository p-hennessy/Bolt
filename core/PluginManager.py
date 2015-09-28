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
        self.findPlugins()
        sys.path.append("plugins")

    def findPlugins(self):
        for file in os.listdir("plugins"):
            if(file.endswith(".py") and not file.startswith('__')):
                name = os.path.splitext(file)[0]
                self.plugins[name] = {"instance": None, "status": "Disabled"}

    def getPluginNames(self):
        return self.plugins.keys()

    def getPlugin(self, pluginName):
        if(pluginName in self.plugins):
            return self.plugins[pluginName]
        else:
            return None

    def exists(self, pluginName):
        return pluginName in self.plugins

    def status(self, pluginName):
        return self.getPlugin(pluginName)["status"]

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
            pluginCanadiate = imp.find_module(moduleName)
            pluginModule = imp.load_module(moduleName, *pluginCanadiate)
        except ImportError as e:
            self.logger.error(e)
            return

        plugin = None

        # Find plugin subclass and initialize it
        for name, clazz in inspect.getmembers(pluginModule, inspect.isclass):
            if(name == "Plugin"):
                continue

            if(issubclass(clazz, Plugin)):
                plugin = clazz(self.core, name)
                break
            else:
                self.logger.error("Could not find plugin subclass in module: " + moduleName)
                return

        # Call activate() if it exists
        if( hasattr(plugin, "activate") ):
            plugin.activate()

        # Register plugin commands and events
        for name, callback in inspect.getmembers(plugin, inspect.ismethod):
            if( hasattr(callback, "is_command") ):
                self.core.command.register(getattr(callback, "trigger"), callback)

            if( hasattr(callback, "is_subscriber") ):
                self.core.event.subscribe(getattr(callback, "event"), callback)

            if( hasattr(callback, "is_publisher") ):
                self.core.event.register(getattr(callback, "event"))

        # Push plugin to our hashtable
        self.plugins[plugin.name] = {"instance":plugin, "status": "Enabled"}
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
        plugin = self.plugins[pluginName]

        # Unregister plugin commands and events
        for name, callback in inspect.getmembers(plugin, inspect.ismethod):
            if( hasattr(callback, "is_command") ):
                self.core.command.unregister(callback.__name__)

        # Remove from our hashtable
        self.plugins[plugin.name] = {"instance":None, "status": "Disabled"}
        self.logger.info("Unloaded plugin \"" + plugin.name + "\"")

    def reload(self, pluginName):
        """
            Summary:
                Wrapper for unload + load

            Args:
                pluginName (str): Name of the plugin class instance to be reloaded

            Returns:
                None
        """

        plugin = self.getPlugin(pluginName)

        if not plugin:
            return

        elif(plugin['status'] == 'Disabled'):
            self.load(pluginName)
        else:
            self.unload(pluginName)
            self.load(pluginName)
