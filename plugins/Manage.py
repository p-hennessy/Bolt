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

from arcbot.Plugin import Plugin
from arcbot.Decorators import *
from arcbot.Discord import events
from arcbot.Discord import api
from arcbot.Discord import embed_intent

import time
import re
from collections import defaultdict
from datetime import timedelta

class Manage(Plugin):
    def activate(self):
        self.login_time = 1466978500
        self.session_time = 1466978500

    @command("^ping")
    def ping(self, event):
        """
            Description: Basic command to verfiy bot can respond to chat messges
            Usage: arcbot ping
        """
        self.say(event.channel_id, "Pong")

    @command("^trigger$", trigger="?")
    def trigger(self, event):
        """
            Description: Prints out the default trigger for the bot
            Usage: ?trigger
        """
        self.say(event.channel_id, f"My default trigger is `{self.core.trigger}`")

    @command("^(help|commands)$")
    def help(self, event):
        """
            Description: Well this is meta. Prints out all the commands and plugins the bot knows about
            Usage: arcbot [help, commands]
        """
        start = time.monotonic()
        commands = defaultdict(list)

        for _, command in self.core.command.commands.items():
            command_class = type(command.callback.__self__).__name__
            command_name = command.callback.__name__

            commands[command_class].append(command_name)

        fields = []

        for name, items in commands.items():
            fields.append({
                "name": name + ":",
                "value": "\n".join([f"`{i}`" for i in items])
            })


        embed = {
            "title": f":information_source: {self.core.name} Help",
            "description": "**Usage**:\nTo get a help page, type: ```html\narcbot help <plugin>.<command>```",
            "color": embed_intent.INFO,
            'fields': fields,
            "footer": {
              "text": f"⏱ {timedelta(seconds=time.monotonic()-start)}"
            }
        }

        self.say(event.channel_id, embed=embed)


    @command("help ([A-Za-z]+).([A-Za-z]+)")
    def help_page(self, event):
        """
            Description: Well this is meta. Prints out useful help messages
            Usage: arcbot help <plugin>.<command>
        """
        start = time.monotonic()

        for _, command in self.core.command.commands.items():
            command_class = type(command.callback.__self__).__name__
            command_name = command.callback.__name__

            if command_class.lower() == event.arguments[1].lower() and command_name.lower() == event.arguments[2].lower():
                help_name = f"plugins.{command_class}.{command_name}"
                help_access_level = command.access
                help_description = "Not documented"
                help_usage = "Not documented"

                if not command.callback.__doc__:
                    self.say(event.channel_id, f"No help page found for `{command_class}.{command_name}`")
                    return

                for line in command.callback.__doc__.splitlines():
                    line = line.strip("\n ")

                    if re.search("Description:", line):
                        help_description = line.split(":")[1]
                    elif re.search("Usage:", line):
                        help_usage = line.split(":")[1]

                embed = {
                    "title": f":information_source: {self.core.name} Help",
                    "description": f"\n*{help_name}*\n\n**Description**\n{help_description}",
                    "color": int("7289da", 16),
                    'fields': [
                        {'name': 'Usage', 'value': f"`{help_usage}`", "inline": True},
                        {'name': 'Access', 'value': f"`{help_access_level}`", "inline": True}
                    ],
                    "footer": {
                      "text": f"⏱ {timedelta(seconds=time.monotonic()-start)}"
                    }
                }

                self.say(event.channel_id, embed=embed)
                break


    @command("^list plugins$")
    def list_plugins(self, event):
        start = time.monotonic()

        plugins = self.core.plugin.list()
        plugins = sorted(plugins.items())

        names = "".join([name + "\n" for name, meta in plugins])
        statuses = "".join([meta['status'] + "\n" for name, meta in plugins])

        embed = {
            "color": int("7289da", 16),
            'fields': [
                {'name': 'Name', 'value': names, "inline": True},
                {'name': 'Status', 'value': statuses, "inline": True}
            ],
            "footer": {
              "text": f"⏱ {timedelta(seconds=time.monotonic()-start)}"
            }
        }

        self.say(event.channel_id, embed=embed)

    @command("^(enable|disable) plugin ([A-Za-z]+)$")
    def manage_plugin(self, event):
        plugins = self.core.plugin.list()

        plugin = event.arguments[2]
        action = event.arguments[1]

        if plugin in plugins:
            if action == "enable":
                if plugins[plugin]['status'] == "Disabled":
                    self.core.plugin.load(plugin)
                    self.say(event.channel_id, f"Enabled plugin: **{plugin}**")
                else:
                    self.say(event.channel_id, f"{plugin} is already enabled")

            elif action == "disable":
                if plugins[plugin]['status'] == "Enabled":
                    self.core.plugin.unload(plugin)
                    self.say(event.channel_id, f"Disabled plugin: **{plugin}**")
                else:
                    self.say(event.channel_id, f"{plugin} is already disabled")
        else:
            self.say(event.channel_id, "I don't have a plugin by that name.")


    @command("^uptime$")
    def uptime(self, event):
        """
            Description: Show how long bot has been connected
            Usage: arcbot uptime
        """
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

        self.say(event.channel_id, f"I've been connected for: **{readable_time(uptime)}**")
