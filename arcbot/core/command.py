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

from .event import Events
import threading
import re
import logging
logger = logging.getLogger(__name__)

class Command():
    def __init__(self, pattern, callback, trigger="", access=0):
        self.pattern  = pattern
        self.access   = access
        self.callback = callback
        self.trigger  = trigger

    def __str__(self):
        return self.callback.__name__

    def invoke(self, event):
        self.callback(event)

class CommandManager():
    def __init__(self, core):
        self.commands = {}
        self.core = core

        self.core.events.subscribe(Events.MESSAGE_CREATE, self.check)

    def check(self, event):
        """
            Checks if an incoming message is a command
            Invokes any command that matches the criteria
        """
        # Ignore our own messages
        if event.author.id == self.core.backend.id:
            return

        for _, command in self.commands.items():
            if event.content.startswith(command.trigger):
                content = event.content.replace(command.trigger, "", 1)
                match = re.search(command.pattern, content)

                if match:
                    setattr(event, "arguments", match)
                    self.core.thread_pool.queue(command.invoke, event)


    def register(self, pattern, callback, trigger="", access=0, silent=False):
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
