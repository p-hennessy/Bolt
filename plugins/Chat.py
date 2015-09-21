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

        # Class level variables
        self.loginTime = 0

        # Register plugin-level commands
        commands = [
            ["^ping", self.ping, 0],
            ["^whoami", self.whoami, 0],
            ["^help", self.help, 0],
            ["^uptime", self.uptime, 0]
        ]

        for command in commands:
            self.core.command.register( *command )

        # Subscribe to core events
        self.core.event.subscribe("connection.login", self.startTimer)

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

        command = self.core.command.find(message.text[5:])

        if(command):
            self.core.connection.send(command.help(), message.channel)
        else:
            self.core.connection.send("Sorry, I don't have that command.",message.channel)

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
                readable += str(days) + " days "
            if(hours > 0):
                readable += str(hours) + "hours "
            if(minutes > 0):
                readable += str(minutes) + " minutes "
            if(seconds > 0):
                readable += str(seconds) + " seconds "

            return readable

        self.core.connection.send("I have been connected for: " + readableTime(uptime), message.channel)
