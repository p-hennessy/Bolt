"""
    Class Name : PluginManager

    Description:
        Manages loading and unload plugins
            Will bootstrap plugin commands and events when they're loaded

    Contributors:
        - Patrick Hennessy

    License:
        CL4M-B0T is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import sys
import imp
import logging
import inspect

from core.Plugin import Plugin

class PluginManager():
    def __init__(self, core):
        self.core = core
        self.plugins = {}
        self.logger = logging.getLogger("core.PluginManager")
        sys.path.append("plugins")

    def load(self, moduleName):
        """
            Take a file name and loads the module, and initializes it
        """

        try:
            pluginCanadiate = imp.find_module("Chat")
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

        # Push plugin to our hashtable
        self.plugins[plugin.name] = plugin

    def unload(self, pluginName):
        pass

    def reload(pluginName):
        pass
