"""
    Class Name : Command

    Description:
        Manager for commands

    Contributors:
        - Patrick Hennessy

    License:
        CL4M-B0T is free software: you can redistribute it and/or modify it
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

    def help(self):
        docstring = self.callback.__doc__

        if(docstring):
            return docstring
        else:
            return "That command is currently undocumented"

class CommandManager():
    def __init__(self, core):
        self.commands = {}
        self.lock = threading.Lock()
        self.core = core

    def getCommands(self):
        return self.commands

    def register(self, invocation, callback, access=0):
        name = callback.__name__

        if( name in self.commands ):
            return
        else:
            self.commands[name] = Command(
                invocation,
                callback,
                access
            )

    def unregister(self, commandName):
        for command in self.commands:
            if(command.invocation == commandName):
                self.commands.remove(command)
