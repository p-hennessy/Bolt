"""
    Plugin Name : Chat
    Plugin Version : 1.0

    Description:
        Gives basic commands to the bot

    Contributors:
        - Patrick Hennessy

    License:
        CL4M-B0T is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *

import time

class Manage(Plugin):

    def activate(self):
        pass

    @subscriber("connect")
    def startTimer(self, *args, **kwargs):
        self.loginTime = time.time()

    @command("^help")
    def help(self, msg):
        pass

    @command("^plugin")
    def plugin(self, msg):
        args = msg.asArgs()

        if(len(args) > 1):

            # List plugins / status
            if(args[1] == 'list'):
                pluginList = self.core.plugin.getPluginNames()
                padding = len(max(pluginList)) + 1

                returnMsg = ""
                for pluginName in pluginList:
                    returnMsg += "\n\t[" + self.core.plugin.status(pluginName) + "]\t" + pluginName

                self.say(msg.channel, "My plugins are: " + returnMsg)
                return

            else:
                if(len(args) < 3):
                    self.say(msg.channel, "Not enough arguments")
                    return

                # Get the plugin name
                if(self.core.plugin.exists(args[1])):
                    # Check operation
                    if(args[2] == "status"):
                        self.say(msg.channel, "Plugin " + args[1] + " [" + self.core.plugin.status(args[1]) + "]")
                    elif(args[2] == "reload"):
                        self.core.plugin.reload(args[1])
                        self.say(msg.channel, "Reloading plugin")
                    elif(args[2] == "disable"):
                        pass
                    elif(args[2] == "enable"):
                        pass
                    else:
                        self.say(msg.channel, "Operation doesnt exist")
                else:
                    self.say(msg.channel, 'I don\'t have a plugin by that name')

    @command("^ping")
    def ping(self, msg):
        self.say(msg.channel, "Pong")

    @command("^uptime")
    def uptime(self, msg):
        uptime = time.time() - self.loginTime

        def readableTime(elapsedTime):
            readable = ""

            days = int(elapsedTime / (60 * 60 * 24))
            hours = int((uptime / (60 * 60)) % 24)
            minutes = int((uptime % (60 * 60)) / 60)
            seconds = int(uptime % 60)

            if(days > 0):       readable += str(days) + " days "
            if(hours > 0):      readable += str(hours) + "hours "
            if(minutes > 0):    readable += str(minutes) + " minutes "
            if(seconds > 0):    readable += str(seconds) + " seconds "

            return readable

        self.say(msg.channel, "I've been connected for: **" + readableTime(uptime) + "**")
