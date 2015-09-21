"""
    Class Name : Command

    Description:
        Manager for commands

    Contributors:
        - Patrick Hennessy

    License:
        PhilBot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import threading
import re

class Command():
    def __init__(self, invocation, callback, access=0, useDefaultTrigger=False):
        self.invocation = invocation
        self.access = access
        self.useDefaultTrigger = useDefaultTrigger
        self.callback = callback

    def __str__(self):
        return self.invocation

    def getAccess(self):
        return self.access

    def invoke(self, message):
        self.callback(message)

class CommandManager():
    def __init__(self, core):
        self.commands = []
        self.lock = threading.Lock()
        self.core = core

    def getCommands(self):
        return self.commands

    def matchCommands(self, match):
        matches = []

        for command in self.commands:
            if(command.useDefaultTrigger and match.startswith(self.core.botConfig["trigger"]) and re.match(command.invocation, match.split(self.core.botConfig["trigger"])[1])):
                matches.append(command)
            elif(not command.useDefaultTrigger and re.match(command.invocation, match)):
                matches.append(command)

        return matches

    def register(self, invocation, callback, access=0, useDefaultTrigger=False):
        self.commands.append(
            Command(
                invocation,
                callback,
                access,
                useDefaultTrigger
            )
        )

    def unregister(self, commandName):
        self.commands.remove(commandName)
