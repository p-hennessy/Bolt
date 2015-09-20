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

class Command():
    def __init__(self, invocation, callback, trigger=".", access=0):
        self.invocation = invocation
        self.access = access
        self.trigger = trigger
        self.callback = callback

    def __str__(self):
        return self.invocation

    def getAccess(self):
        return self.access

class CommandManager():
    def __init__(self):
        self.commands = []
        self.lock = threading.Lock()

    def getCommands(self):
        pass

    def find(self, commandName):
        for command in self.commands:
            if(commandName.startswith(command.trigger + command.invocation)):
                return command

        return None

    def register(self, command):
        self.commands.append(command)

    def unregister(self, commandName):
        self.commands.remove(commandName)

    def check(self, commandName):
        pass

    def invoke(self, command, rawMsg):
        args = rawMsg.split(command.invocation)[1:]

        return command.callback(args)
