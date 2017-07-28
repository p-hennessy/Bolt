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

from typing import Callable

logger = logging.getLogger(__name__)

class Command():
    def __init__(self, pattern: str, callback: Callable, trigger: str="", access: int=0, silent: bool=False):
        self.pattern  = pattern
        self.access   = access
        self.callback = callback
        self.trigger  = trigger
        self.silent   = silent

    def __str__(self) -> None:
        return self.callback.__name__

    def invoke(self, message: str) -> None:
        self.callback(message)

class CommandManager():
    def __init__(self, core):
        self.commands = {}
        self.core = core

    def check(self, message: str) -> None:
        """
            Checks if an incoming message is a command
            Invokes any command that matches the criteria
        """
        commands = list(self.commands.items())
        for key, command in commands:
            if message.content.startswith(command.trigger):
                content = message.content.replace(command.trigger, "", 1)
                match   = re.search(command.pattern, content)

                if match:
                    if self.core.ACL.getAccess(message.sender) >= command.access:
                        message.content = content
                        message.arguments = match
                        command.invoke(message)
                    elif not command.silent:
                        self.core.connection.reply(message.sender, message.channel, f"Sorry, you need `{command.access}` access to use that command.")

    def register(self, pattern: str, callback: Callable, trigger: str="", access: int=0, silent: bool=False) -> None:
        """
            Pushes command instance to command list
        """
        clazz = type(callback.__self__).__name__
        name = clazz + "." + callback.__name__

        if name in self.commands:
            logger.warning("Duplicate command \"" + clazz + "." + name + "\". Skipping registration.")
            return
        else:
            logger.debug("Registered command \"" +  clazz + "." + name + "\"")

            if trigger is None:
                trigger = ""
            elif trigger == "":
                trigger = self.core.trigger

            self.commands[name] = Command(
                pattern,
                callback,
                trigger=trigger,
                access=access,
                silent=silent
            )

    def unregister(self, command_name: str) -> None:
        """
            Unregisters a command
            Removes command instance from command list
            Command will no longer run when message parser finds a match
        """
        if command_name in self.commands:
            command = self.commands[command_name]

            clazz = type(command.callback.__self__).__name__
            name = clazz + "." + command.callback.__name__

            del self.commands[command_name]
            logger.debug("Unregistered command \"" + name + "\"")

        else:
            logger.warning("Cannot unregister \"" + command_name + "\", command not found.")
