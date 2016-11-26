"""
    Plugin Name : Manage
    Plugin Version : 1.2

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

class Manage(Plugin):
    def activate(self):
        self.login_time = None
        self.session_time = None

    @command("^ping", access=50)
    def ping(self, msg):
        self.say(msg.channel, "Pong")

    @command("^trigger$", trigger="?", access=50)
    def trigger(self, msg):
        self.say(msg.channel, "My default trigger is `" + self.core.trigger + "`")

    @command("^list plugins$", access=50)
    def list_plugins(self, msg):
        plugins = self.core.plugin.list()

        table = []
        for name, meta in sorted(plugins.items()):
            table.append([name, meta['status']])

        output = "**My plugins: **\n\n"
        output += "`{}`".format(tabulate(table, headers=["Name", "Status"], tablefmt="psql", numalign="left"))

        self.say(msg.channel, output)

    @command("^(enable|disable|reload|status) plugin ([A-Za-z]+)$", access=1000)
    def manage_plugin(self, msg):
        plugins = self.core.plugin.list()
        plugin = msg.arguments[1]
        action = msg.arguments[0]

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
                if not plugins[plugin]['status'] == "Disabled":
                    self.core.plugin.reload(plugin)
                    self.say(msg.channel, "Reloaded plugin: **{}**".format(plugin))
        else:
            self.say(msg.channel, "I don't have a plugin by that name.")

    @subscribe("connect")
    def on_connect(self, *args, **kwargs):
        if self.login_time:
            self.session_time = time.time()
        else:
            self.login_time = time.time()

    @command("^uptime$", access=50)
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
