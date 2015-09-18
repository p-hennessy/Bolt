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

from core.Command import Command
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
        self.core.subscribe("recieve.message", self.onMessage)
        self.core.subscribe("recieve.command", self.onMessage)

        # Register plugin-level commands
        commands = [
            Command("ping", self.ping, access=0)
        ]

        for command in commands:
            self.core.registerCommand( command )

    # Destructor, do any garbage collection here
    def __del__(self):
        self.core.unsubscribe("recieve.message")
        self.core.unsubscribe("recieve.command")

    # Entry to the thread
    def startThread(self):
        while not self.kill:
            print "Started ChatPlugin"
            time.sleep(4)

    # Commands Implementations
    def ping(self, *args):
        self.core.say("Pong!")

    # Event Handlers
    def onMessage(self, args):

        timestamp = datetime.datetime.fromtimestamp( float(args["timestamp"]) ).strftime('%m/%d/%Y %H:%M:%S')
        username = self.core.getUserInfo(args["uid"])["user"]["name"]

        print "[" + timestamp + "] <" + username + "> "+ args["text"]
