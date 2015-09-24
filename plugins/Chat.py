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

from core.Decorators import *
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

        # Class level variables
        self.loginTime = 0

        # Register plugin-level commands
        self.core.command.register("^ping", self.ping, 0)
        self.core.command.register("^help", self.help, 0)
        self.core.command.register("^whoami", self.whoami, 0)
        self.core.command.register("^uptime", self.uptime, 0)
        self.core.command.register("^commands", self.commands, 0)

        # Subscribe to core events
        self.core.event.subscribe("connection.login", self.startTimer)

    # For when we want to unload or restart a plugin
    def __del__(self):
        # Unregister plugin commands
        self.core.command.unregister("^ping")
        self.core.command.unregister("^help")
        self.core.command.unregister("^whoami")
        self.core.command.unregister("^uptime")
        self.core.command.unregister("^commands")

        # Unsubscribe from core events
        self.core.event.unsubscribe("connection.login", self.startTimer)

    # Thread logic
    def startThread(self):
        pass

    # Event Implementations
    def startTimer(self, *args):
        self.loginTime = time.time()

    # Commands Implementations
    def ping(self, message):
        """
        Ping
            Returns time in milliseconds to reach the Slack server.
            Arguments: None
        """
        ping = self.core.connection.ping()
        self.core.connection.send("My ping is: " + str(ping) + "ms", message.channel)

    def whoami(self, message):
        """
        Whoami
            Returns relevant information about you and your relation to the bot.
            Arguments: None
        """

        self.core.connection.send(
            "Name: \t" + message.sender.getPreferedName() + "\n" +
            "UID: \t\t" + message.sender.id + "\n" +
            " You have " + str(message.sender.getAccess()) + " access."
        , message.channel)

    def help(self, message):
        """
        Help
            Returns the documentation for a command.
            Arguments: [commandName]
        """
        if(len(message.text[5:]) <= 0):
            self.core.connection.send("Hi " + message.sender.getPreferedName() + ", what can I help you with?", message.channel)
            return

        command = self.core.command.find(message.text[5:])

        if(command):
            self.core.connection.send(command.help(), message.channel)
        else:
            self.core.connection.send("Sorry, I don't have that command.", message.channel)

    def uptime(self, message):
        """
        Uptime
            Returns amount of time the bot has been connected.
            Arguments: None
        """
        uptime = time.time() - self.loginTime

        def readableTime(elapsedTime):
            readable = ""

            days = int(elapsedTime / (60 * 60 * 24))
            hours = int((uptime / (60 * 60)) % 24)
            minutes = int((uptime % (60 * 60)) / 60)
            seconds = int(uptime % 60)

            if(days > 0):
                readable += str(days)
                if(days == 1):
                    readable += " day "
                else:
                    readable += " days "
            if(hours > 0):
                readable += str(hours)
                if(hours == 1):
                    readable += " hour "
                else:
                    readable += " hours "
            if(minutes > 0):
                readable += str(minutes)
                if(minutes == 1):
                    readable += " minute "
                else:
                    readable += " minutes "
            if(seconds > 0):
                readable += str(seconds)
                if(seconds == 1):
                    readable += " second "
                else:
                    readable += " seconds "

            return readable

        self.core.connection.send("I have been connected for: " + readableTime(uptime), message.channel)

    def commands(self, message):
        commandList = ""
        for command in self.core.command.getCommands():
                commandList += command.callback.__name__ + "\n\t"

        self.core.connection.send("I will repond to the following commands:\n\t" + commandList + "\n Type \"help <command>\" for more information", message.channel)
