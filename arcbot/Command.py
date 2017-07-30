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

from arcbot.Discord import events

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

    def invoke(self, event) -> None:
        self.callback(event)

class CommandManager():
    def __init__(self, core):
        self.commands = {}
        self.core = core

        self.core.event.subscribe(events.MESSAGE_CREATE, self.check)

    def check(self, event: dict):
        """
            Checks if an incoming message is a command
            Invokes any command that matches the criteria
        """
        for _, command in self.commands.items():
            if event.content.startswith(command.trigger):
                content = event.content.replace(command.trigger, "", 1)
                match = re.search(command.pattern, content)

                if match:
                    setattr(event, "arguments", match)
                    self.core.workers.queue(command.invoke, event)


    def register(self, pattern: str, callback: Callable, trigger: str="", access: int=0, silent: bool=False):
        """
            Pushes command instance to command list
        """
        clazz = type(callback.__self__).__name__
        name = clazz + "." + callback.__name__

        if name in self.commands:
            logger.warning("Duplicate command \"" + clazz + "." + name + "\". Skipping registration.")
            return
        else:
            logger.debug("Registering command \"" +  clazz + "." + name + "\"")

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

    def unregister(self, command_name: str):
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
