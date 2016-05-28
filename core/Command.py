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
    def __init__(self, pattern, callback, trigger="", access=0, silent=False):
        self.pattern  = pattern
        self.access   = access
        self.callback = callback
        self.trigger  = trigger
        self.silent   = silent

    def __str__(self):
        return self.callback.__name__

    def invoke(self, message):
        self.callback(message)

class CommandManager():
    def __init__(self, core):
        self.commands = {}
        self.core = core

    def check(self, message):
        """
            Summary:
                Checks if an incoming message is a command
                Invokes any command that matches the criteria

            Args:
                message (Message): A message instance from core.Message

            Returns:
                None
        """
        for key, command in self.commands.items():
            if message.content.startswith(command.trigger):
                content = message.content.replace(command.trigger, "", 1)
                match   = re.search(command.pattern, content)

                if match:
                    if self.core.ACL.getAccess(message.sender) >= command.access:
                        message.content = content
                        message.arguments = match
                        command.invoke(message)
                    elif not command.silent:
                        self.core.connection.reply(message.sender, message.channel, "Sorry, you need `{}` access to use that command.".format(command.access))

    def register(self, pattern, callback, trigger="", access=0, silent=False):
        """
            Summary:
                Pushes command instance to command list

            Args:
                pattern (str): Regex that the message parser will match with
                callback (func): Function object that will be invoked when message parser finds a match
                trigger (str): Beginning of the string to denote a command, default is in the config
                access (int): Amount of access required to invoke a command
                silent (bool): Squelch access error messages

            Returns:
                None
        """
        clazz = type(callback.__self__).__name__
        name = clazz + "." + callback.__name__

        if name in self.commands:
            logger.warning("Duplicate command \"" + clazz + "." + name + "\". Skipping registration.")
            return
        else:
            logger.debug("Registered command \"" +  clazz + "." + name + "\"")

            if not trigger:
                trigger = self.core.config.trigger

            self.commands[name] = Command(
                pattern,
                callback,
                trigger=trigger,
                access=access,
                silent=silent
            )

    def unregister(self, command_name):
        """
            Summary:
                Unregisters a command
                Removes command instance from command list
                Command will no longer run when message parser finds a match

            Args:
                command_name (str): Name of the command to unregister

            Returns:
                None
        """
        if command_name in self.commands:
            command = self.commands[command_name]

            clazz = type(command.callback.__self__).__name__
            name = clazz + "." + command.callback.__name__

            del self.commands[command_name]
            logger.debug("Unregistered command \"" + name + "\"")

        else:
            logger.warning("Cannot unregister \"" + command_name + "\", command not found.")
