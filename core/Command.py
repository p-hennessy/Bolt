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

logger = logging.getLogger(__name__)

class Command():
    def __init__(self, invocation, callback, useDefaultTrigger=True, access=0):
        self.invocation = invocation
        self.access = access
        self.callback = callback
        self.useDefaultTrigger = useDefaultTrigger

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

    def checkMessage(self, message):
        """
            Summary:
                Checks if an incoming message is a command
                Invokes any command that matches the criteria

            Args:
                message (str): A message instance from core.Message

            Returns:
                None
        """
        for key, command in list(self.commands.items()):
            # Checks to see if message is a command and uses default trigger defined in conf/settings.py
            if(command.useDefaultTrigger and message.content.startswith(self.core.config.trigger)):
                # Looks at the message content and decide if it matches
                match = re.search(command.invocation, message.content.replace(self.core.config.trigger, "", 1))

                if(match):
                    # Check if user has access to invoke command
                    if(self.core.ACL.getAccess(message.sender) >= command.access):
                        message.content = message.content.replace(self.core.config.trigger, "", 1)
                        message.setMatch(match)
                        command.invoke(message)
                    else:
                        self.core.connection.reply(message, "Sorry, you need {} access to use that command.".format(command.access))

            # Will invoke command if it matches command invocation and doesn't use trigger
            elif(command.useDefaultTrigger == False):
                match = re.search(command.invocation, message.content)
                if(match):
                    if(self.core.ACL.getAccess(message.sender) >= command.access):
                        message.setMatch(match)
                        command.invoke(message)
                    else:
                        self.core.connection.reply(message, "Sorry, you need {} access to use that command.".format(command.access))

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

    def register(self, invocation, callback, useDefaultTrigger=True, access=0):
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

        try:
            clazz = callback.im_class.__name__
        except:
            clazz = type(callback.__self__).__name__

            name = clazz + "." + callback.__name__

        if( name in self.commands ):
            logger.warning("Duplicate command \"" + clazz + "." + name + "\". Skipping registration.")
            return
        else:
            logger.debug("Registered command \"" +  clazz + "." + name + "\"")

            self.commands[name] = Command(
                invocation,
                callback,
                useDefaultTrigger,
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

            try:
                clazz = command.callback.im_class.__name__
            except:
                clazz = type(command.callback.__self__).__name__

            name = clazz + "." + command.callback.__name__

            del self.commands[commandName]
            logger.debug("Unregistered command \"" + clazz + "." + name + "\"")

        else:
            logger.warning("Cannot unregister \"" + commandName + "\", command not found.")
