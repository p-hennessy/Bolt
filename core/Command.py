"""
    Class Name : Command

    Description:
        Manager for commands

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import threading
import re
import logging
import six

logger = logging.getLogger(__name__)

class Command():
    def __init__(self, invocation, callback, access=0):
        self.invocation = invocation
        self.access = access
        self.callback = callback

    def __str__(self):
        return self.invocation

    def getAccess(self):
        return self.access

    def invoke(self, message):
        self.callback(message)

    def help(self):
        docstring = self.callback.__doc__

        if(docstring):
            return docstring
        else:
            return "That command is currently undocumented"

class CommandManager():
    def __init__(self, core):
        self.commands = {}
        self.core = core

    def check(self, message):
        if(message.content.startswith(self.core.config.trigger)):
            for key, command in six.iteritems(self.commands):
                if(re.search(command.invocation, message.content[1:])):
                    command.invoke(message)
                    return

    def getCommands(self):
        """
            Summary:
                Returns command hashtable

            Args:
                None

            Returns:
                (dict): Hashtable containing Command instances
        """
        return self.commands

    def getCommand(self, commandName):
        """
            Summary:
                Returns a Command instance

            Args:
                commandName (str): Name of command to get

            Returns:
                (Command): Instance of Command
        """
        if(commandName in self.commands):
            return self.commands[commandName]
        else:
            return None

    def register(self, invocation, callback, access=0):
        """
            Summary:
                Registers a command
                Pushes command instance to hashtable

            Args:
                invocation (str): Regex that the message parser will match with
                callback (func): Function object that will be invoked when message parser finds a match

            Returns:
                None
        """
        import pprint
        name = callback.__name__
        try:
            clazz = callback.im_class.__name__
        except:
            clazz = type(callback.__self__).__name__

        if( name in self.commands ):
            logger.warning("Duplicate command \"" + clazz + "." + name + "\". Skipping registration.")
            return
        else:
            logger.debug("Registered command \"" +  clazz + "." + name + "\"")

            self.commands[name] = Command(
                invocation,
                callback,
                access
            )

    def unregister(self, commandName):
        """
            Summary:
                Unregisters a command
                Removes command instance to hashtable
                Command will no longer run when message parser finds a match

            Args:
                commandName (str): Name of the command to unregister

            Returns:
                None
        """
        if(commandName in self.commands):
            command = self.commands[commandName]

            name = command.callback.__name__
            clazz = command.callback.im_class.__name__

            del self.commands[commandName]
            logger.debug("Unregistered command \"" + clazz + "." + name + "\"")

        else:
            logger.warning("Cannot unregister \"" + commandName + "\", command not found.")
