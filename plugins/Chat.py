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

import threading
import datetime

from core.Command import *

# Init is how every plugin is invoked
def init(core):
    chatThread = Chat(core)
    chatThread.start()

    return chatThread

# This will be called so we can safely exit our threads and do any garbage collection
def destroy():
    pass

class Chat(threading.Thread):
    def __init__(self, core):

        # Call super constructor
        super(Chat, self).__init__()

        # Save core instance
        self.core = core

        # Subsrcribe to Core events
        self.core.subscribe("recieve.message", self.onMessage)
        self.core.subscribe("recieve.command", self.onMessage)

        # Register plugin-level commands
        commands = [
            Command("ping", self.ping, access=0)
        ]

        for command in commands:
            self.core.registerCommand( command )

    def run(self):
        pass

    # Commands Implementations
    def ping(self, *args):
        self.core.say("Pong!")

    # Event Handlers
    def onMessage(self, args):

        timestamp = datetime.datetime.fromtimestamp( float(args["timestamp"]) ).strftime('%m/%d/%Y %H:%M:%S')
        username = self.core.getUserInfo(args["uid"])["user"]["name"]

        print "[" + timestamp + "] <" + username + "> "+ args["text"]
