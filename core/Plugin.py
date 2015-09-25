"""
    Class Name : Plugin

    Description:
        Superclass for which all plugins are derived
        Handles thread-level exception publishing

    Contributors:
        - Patrick Hennessy

    License:
        PhilBot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import sys
import imp
import logging
import inspect

class Plugin(object):
    logger = None

    def __init__(self, core, name):
        self.core = core
        self.name = name

        logger = logging.getLogger("plugins." + self.name)
        logger.info("Plugin: " + self.name)


class PluginManager():
    def __init__(self, core):
        self.core = core
        self.plugins = {}
        self.logger = logging.getLogger("core.PluginManager")
        sys.path.append("plugins")

    def validatePlugin(self, module):
        """
            Will perform sanity checks on a potential plugin
        """

        # Check for metadata object
        if not(hasattr(module, "Metadata")):
            self.logger.error(module.__name__ + " has no Metadata object.")
            return False

        # Check if metadata object is a dict
        if not(isinstance(module.Metadata, dict)):
            self.logger.error(module.__name__ + " Metadata object is not type dict.")
            return False

        # Check for all keys in metadata object
        if not(set(module.Metadata.keys()) == set(["Name", "Description", "Version", "Entrypoint"])):
            keyDiff = list(set(["Name", "Description", "Version", "Entrypoint"]) - set(module.Metadata.keys()))
            self.logger.error(module.__name__ + " Metadata object is missing keys: " + str(keyDiff) )
            return False

        # Check if we already have this module loaded
        if (module.Metadata["Name"] in self.plugins):
            self.logger.error(module.__name__ + " plugin already loaded")
            return False

        # Check that entry point is a Plugin subclass
        entrypoint = getattr(module, module.Metadata["Entrypoint"])
        if not(issubclass(entrypoint, Plugin)):
            self.logger.error(entrypoint.__name__ + " is not subclass of Plugin")
            return False

        return True

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

        if(self.validatePlugin(pluginModule)):
            # Get plugin metadata
            pluginMetadata = pluginModule.Metadata
            entrypoint = getattr(pluginModule, pluginMetadata["Entrypoint"])

            # Plugin class instance
            pluginInstance = entrypoint(self.core, pluginMetadata["Name"])

            # Call activate() if it exists
            if( hasattr(entrypoint, "activate") ):
                pluginInstance.activate()

            # Register plugin commands and events
            for name, callback in inspect.getmembers(pluginInstance, inspect.ismethod):
                if( hasattr(callback, "is_command") ):
                    self.core.command.register(getattr(callback, "trigger"), callback)

            # Push plugin to our hashtable
            self.plugins[pluginInstance.name] = pluginInstance

    def unload(self, pluginName):
        pass

    def reload(pluginName):
        pass
