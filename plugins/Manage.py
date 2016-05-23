"""
    Plugin Name : Manage
    Plugin Version : 1.1

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
from tabulate import tabulate

ACCESS = {
    "speak"     :   999,
    "trigger"   :   50,
    "plugin"    :   1000,
    "help"      :   1000,
    "ping"      :   50,
    "uptime"    :   50
}

class Manage(Plugin):

    @subscribe("connect")
    def startTimer(self, *args, **kwargs):
        self.login_time = time.time()

    @command("^say (.*)$", access=ACCESS['speak'])
    def speak(self, msg):
        self.say(msg.channel, msg.arguments[0])

    @command("^\?trigger$", useDefaultTrigger=False, access=ACCESS["trigger"])
    def trigger(self, msg):
        self.say(msg.channel, "My trigger is `" + self.core.config.trigger + "`")

    @command("^list plugins", access=ACCESS["plugin"])
    def plugin_list(self, msg):
        plugins = self.core.plugin.list()

        table = []
        for name, meta in sorted(plugins.items()):
            table.append([name, meta['status']])

        output = "**My plugins: **\n\n"
        output += "`{}`".format(tabulate(table, headers=["Name", "Status"], tablefmt="psql", numalign="left"))

        self.say(msg.channel, output)

    @command("^(enable|disable|reload|status) plugin ([A-Za-z]+)", access=ACCESS["plugin"])
    def plugin_do(self, msg):
        args = msg.arguments
        plugins = self.core.plugin.list()
        plugin = args[1]
        action = args[0]

        if plugin in plugins:
            if action == "enable":
                if plugins[plugin]['status'] == "Disabled":
                    self.core.plugin.load(plugin)
                    self.say(msg.channel, "Enabled plugin: **{}**".format(plugin))
                else:
                    self.say(msg.channel, "{} is already enabled".format(plugin))

            elif action == "disable":
                if plugins[plugin]['status'] == "Enabled":
                    self.core.plugin.unload(plugin)
                    self.say(msg.channel, "Disabled plugin: **{}**".format(plugin))
                else:
                    self.say(msg.channel, "{} is already disabled".format(plugin))

            elif action == "reload":
                if plugins[plugin]['status'] == "Disabled":
                    self.core.plugin.reload(plugin)
                    self.say(msg.channel, "Reloaded plugin: **{}**".format(plugin))
        else:
            self.say(msg.channel, "I don't have a plugin by that name.")

    @command("^ping$", access=ACCESS["ping"])
    def ping(self, msg):
        self.say(msg.channel, "Pong")

    @command("^uptime", access=ACCESS["uptime"])
    def uptime(self, msg):
        uptime = time.time() - self.login_time

        def readable_time(elapsed):
            readable = ""

            days = int(elapsed / (60 * 60 * 24))
            hours = int((uptime / (60 * 60)) % 24)
            minutes = int((uptime % (60 * 60)) / 60)
            seconds = int(uptime % 60)

            if(days > 0):       readable += str(days) + " days "
            if(hours > 0):      readable += str(hours) + " hours "
            if(minutes > 0):    readable += str(minutes) + " minutes "
            if(seconds > 0):    readable += str(seconds) + " seconds "

            return readable

        self.say(msg.channel, "I've been connected for: **" + readable_time(uptime) + "**")
