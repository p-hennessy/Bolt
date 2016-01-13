"""
    Plugin Name : Chat
    Plugin Version : 1.0

    Description:
        Gives basic commands to the bot

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *

import time
import shlex
import traceback

ACCESS = {
    "setStatus" :   1000,
    "whoami"    :   50,
    "whois"     :   50,
    "channelid" :   999,
    "trigger"   :   50,
    "plugin"    :   1000,
    "ping"      :   50,
    "uptime"    :   50
}

class Manage(Plugin):

    def activate(self):
        pass

    @subscriber("connect")
    def startTimer(self, *args, **kwargs):
        self.loginTime = time.time()

    @command("^set status (.+)", access=ACCESS["setStatus"])
    def setStatus(self, msg):
        status = msg.getMatches()[0]

        self.core.connection._Discord__writeSocket({
            "op":3,
            "d":{
                "idle_since":None,
                "game": {
                    "name": status
                }
            }
        })

    @command("^whois <@([0-9]+)>", access=ACCESS["whois"])
    def whois(self, msg):
        target = msg.getMatches()[0]
        access = self.core.ACL.getAccess(target)

        self.say(msg.channel, "User ID\t`{}`\nAccess:\t`{}`".format(msg.sender, access))

    @command("^whoami", access=ACCESS["whoami"])
    def whoami(self, msg):
        access = self.core.ACL.getAccess(msg.sender)

        self.reply(msg, "\nUser ID\t`{}`\nAccess:\t`{}`".format(msg.sender, access))

    @command("^channelid", access=ACCESS["channelid"])
    def channelid(self, msg):
        self.say(msg.channel, "ID of current channel is: `{}`".format(msg.channel))

    @command("^\?trigger$", useDefaultTrigger=False, access=ACCESS["trigger"])
    def trigger(self, msg):
        self.say(msg.channel, "My trigger is `" + self.core.config.trigger + "`")

    @command("^plugin (list|[A-Za-z]+ (enable|disable|reload|status))", access=ACCESS["plugin"])
    def plugin(self, msg):
        """
        *Plugin* : Allows one to manage plugins
        Usage:
        plugin list
        plugin [name] [enable|disable|reload|status]
        """
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
                        self.say(msg.channel, "Reloading " + args[1] + " plugin")
                    elif(args[2] == "disable"):
                        self.core.plugin.unload(args[1])
                        self.say(msg.channel, "Disabled " + args[1] + " plugin")
                    elif(args[2] == "enable"):
                        self.core.plugin.load(args[1])
                        self.say(msg.channel, "Enabled " + args[1] + " plugin")
                    else:
                        self.say(msg.channel, "Operation doesnt exist")
                else:
                    self.say(msg.channel, 'I don\'t have a plugin by that name')

    @command("^ping$", access=ACCESS["ping"])
    def ping(self, msg):
        """
        *Ping* : Basic command to check if bot responds to messages
        """
        self.say(msg.channel, "Pong")

    @command("^uptime", access=ACCESS["uptime"])
    def uptime(self, msg):
        """
        *Uptime*: Will show a human-readable time duration since the bot logged in.
        """
        uptime = time.time() - self.loginTime

        def readableTime(elapsedTime):
            readable = ""

            days = int(elapsedTime / (60 * 60 * 24))
            hours = int((uptime / (60 * 60)) % 24)
            minutes = int((uptime % (60 * 60)) / 60)
            seconds = int(uptime % 60)

            if(days > 0):       readable += str(days) + " days "
            if(hours > 0):      readable += str(hours) + " hours "
            if(minutes > 0):    readable += str(minutes) + " minutes "
            if(seconds > 0):    readable += str(seconds) + " seconds "

            return readable

        self.say(msg.channel, "I've been connected for: **" + readableTime(uptime) + "**")
