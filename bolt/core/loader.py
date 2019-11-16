"""
    Description:
        Singleton responsible for loading plugins into the botself.
        
        Plugins can currently be loaded from:
            - Single .py files
            - Folder / module
            - Zip files

    Contributors:
        - Patrick Hennessy
"""
from bolt.core.plugin import Plugin

import os
import logging
import logging.handlers
import inspect
import importlib
import sys
import zipfile
import zipimport


class Loader():
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    def load_plugins(self):
        plugin_dir = os.path.abspath(self.bot.config.plugin_dir)
        self.add_module_path(plugin_dir)
                
        for file in os.listdir(plugin_dir):
            file_path = os.path.join(plugin_dir, file)
            
            if zipfile.is_zipfile(file_path):
                self.load_plugin_from_zip(file_path)
            elif os.path.isfile(file_path):
                self.load_plugin_from_file(file_path)
            elif os.path.isdir(file_path):
                self.load_plugin_from_module(file_path)

    def load_plugin_module(self, module):
        for name, clazz in inspect.getmembers(module, inspect.isclass):
            if issubclass(clazz, Plugin) and name != "Plugin":
                plugin = clazz(self.bot)
                plugin.load()

                self.bot.plugins.append(plugin)
                break
        else:
            self.logger.warning(f"Failed to load \"{module.__file__}\". Invalid Bolt plugin, missing a Plugin subclass")

    def unload_plugin(self, name):
        for index, plugin in enumerate(self.plugins):
            if plugin.name == name:
                plugin = self.bot.plugins.pop(index)
                plugin.unload()
                break
        else:
            self.logger.warning(f"No plugin loaded named: \"{name}\", cannot unload.")
    
    def add_module_path(self, path):
        path = os.path.abspath(path)
        
        if path not in sys.path:
            self.logger.debug(f"Added {path} to module search path.")
            sys.path.append(path)
        else:
            self.logger.debug(f"Path {path} already included in module search path.")
    
    def load_plugin_from_file(self, path):
        name = path.split('/')[-1].split('.')[0]
        path = os.path.abspath(path)
        module_spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        self.load_plugin_module(module)

    def load_plugin_from_module(self, path):
        name = os.path.basename(path)
        module_loader = importlib.find_loader(name)
        module_spec = importlib.util.spec_from_loader(name, module_loader)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        self.load_plugin_module(module)

    def load_plugin_from_zip(self, path):
        name = path.split('/')[-1].split('.')[0]
        path = os.path.abspath(path)
        zipper = zipimport.zipimporter(path)
        module = zipper.load_module(name)
        self.load_plugin_module(module)
