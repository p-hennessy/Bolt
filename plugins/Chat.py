"""
    Plugin Name : Chat
    Plugin Version : 1.0

    Description:
        Gives basic commands to the bot

    Contributors:
        - Patrick Hennessy

    License:
        PhilBot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import datetime
import time

from core.Plugin import Plugin

# Init is how every plugin is invoked
def init(core):
    pluginThread = Chat(core)
    pluginThread.daemon = True
    pluginThread.start()

    return pluginThread

class Chat(Plugin):
    def __init__(self, core):
        # Call super constructor
        super(Chat, self).__init__(core, "ChatPlugin")

        # Subsrcribe to Core events
        self.core.event.subscribe("recieve.message", self.onMessage)

        # Register plugin-level commands
        commands = [
            ["^ping", self.ping, 0],
            ["^whoami", self.whoami, 0],
        ]

        for command in commands:
            self.core.command.register( *command )

    # Entry to the thread
    def startThread(self):
        pass

    # Commands Implementations
    def ping(self, message):
        ping = self.core.connection.ping()
        self.core.connection.send("My ping is: " + str(ping) + "ms", message.channel)

    def whoami(self, message):
        self.core.connection.send(
            "Name: \t" + message.sender.getPreferedName() + "\n" +
            "UID: \t\t" + message.sender.id + "\n" +
            " You have " + str(message.sender.getAccess()) + " access."
        , message.channel)

    # Event Handlers
    def onMessage(self, args):
        pass