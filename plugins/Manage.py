"""
    Plugin Name : Manage

    Description:
        Gives basic commands to the bot

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""
from arcbot import events
from arcbot import Plugin
from arcbot import webhook, command, subscribe
from arcbot import colors

from arcbot.utils import Timer

import time
import re
from collections import defaultdict
from datetime import timedelta

class Manage(Plugin):

    @command("^ping")
    def ping(self, event):
        """
            Description: Basic command to verfiy bot can respond to chat messges
            Usage: arcbot ping
        """
        self.say(event.channel_id, f":zap: **{self.bot.backend.ping}**ms")

    @command("^trigger$", trigger="?")
    def trigger(self, event):
        """
            Description: Prints out the default trigger for the bot
            Usage: ?trigger
        """
        self.say(event.channel_id, f"My default trigger is `{self.bot.config.trigger}`")

    @command("^(help|commands)$")
    def help(self, event):
        """
            Description: Well this is meta. Prints out all the commands and plugins the bot knows about
            Usage: arcbot [help, commands]
        """
        with Timer() as timer:
            commands = defaultdict(list)

            for _, command in self.bot.commands.commands.items():
                command_class = type(command.callback.__self__).__name__
                command_name = command.callback.__name__

                commands[command_class].append(command_name)

            fields = []
            for name, items in commands.items():
                fields.append({
                    "name": name + ":",
                    "value": "\n".join([f"• `{i}`" for i in items]),
                    "inline": True
                })

            embed = {
                "title": f":information_source: {self.bot.config.name} Help",
                "description": f"**Usage**:\nTo get a help page, type: ```html\n{self.bot.config.trigger} help <plugin>.<command>```",
                "color": colors.INFO,
                'fields': fields,
                "footer": {
                  "text": f"⏰ {timer.delta}ms | 🔌 Manage.help"
                }
            }
            self.say(event.channel_id, embed=embed)

    @command("^help ([A-Za-z]+)$")
    def help_error(self, event):
        with Timer() as timer:
            embed = {
                "title": f":octagonal_sign: Error",
                "description": f"Use the right command silly:\n\n```html\narcbot help <plugin>.<command>```",
                "color": colors.ERROR,
                "footer": {
                  "text": f"⏰ {timer.delta}ms | 🔌 Manage.help_error"
                }
            }
            self.say(event.channel_id, "Use the right command silly: ", embed=embed)

    @command("^help ([A-Za-z]+).([A-Za-z_]+)$")
    def help_page(self, event):
        """
            Description: Well this is meta. Prints out useful help messages
            Usage: arcbot help <plugin>.<command>
        """
        with Timer() as timer:
            for _, command in self.bot.commands.commands.items():
                command_class = type(command.callback.__self__).__name__
                command_name = command.callback.__name__

                if command_class.lower() == event.arguments[1].lower() and command_name.lower() == event.arguments[2].lower():
                    help_name = f"plugins.{command_class}.{command_name}"
                    help_access_level = command.access
                    help_description = "Not documented"
                    help_usage = "Not documented"

                    if not command.callback.__doc__:
                        embed = {
                            "title": f":octagonal_sign: Error",
                            "description": f"No help page found for `{command_class}.{command_name}`",
                            "color": colors.ERROR,
                            "footer": {
                              "text": f"⏰ {round(timedelta(seconds=time.monotonic()-start).microseconds/1000, 3)}ms | 🔌 Manage.help_page"
                            }
                        }

                        self.say(event.channel_id, embed=embed)
                        return

                    for line in command.callback.__doc__.splitlines():
                        line = line.strip("\n ")

                        if re.search("Description:", line):
                            help_description = line.split(":")[1]
                        elif re.search("Usage:", line):
                            help_usage = line.split(":")[1]

                    embed = {
                        "title": f":information_source: {self.bot.config.name} Help",
                        "description": f"\n*{help_name}*\n\n**Description**\n{help_description}",
                        "color": colors.INFO,
                        'fields': [
                            {'name': 'Usage', 'value': f"`{help_usage}`", "inline": True},
                            {'name': 'Access', 'value': f"`{help_access_level}`", "inline": True}
                        ],
                        "footer": {
                            "text": f"⏰ {timer.delta}ms | 🔌 Manage.help_page"
                        }
                    }

                    self.say(event.channel_id, embed=embed)
                    break

    @command("^list plugins$")
    def list_plugins(self, event):
        with Timer() as timer:
            plugins = self.bot.plugins.list()
            plugins = sorted(plugins.items())

            names = "".join([name + "\n" for name, meta in plugins])
            statuses = "".join([meta['status'] + "\n" for name, meta in plugins])

            embed = {
                "color": colors.INFO,
                'fields': [
                    {'name': 'Name', 'value': names, "inline": True},
                    {'name': 'Status', 'value': statuses, "inline": True}
                ],
                "footer": {
                    "text": f"⏰ {timer.delta}ms | 🔌 Manage.list_plugins"
                }
            }
            self.say(event.channel_id, embed=embed)

    # @command("^(enable|disable) plugin ([A-Za-z]+)$")
    # def manage_plugin(self, event):
    #     plugins = self.core.plugin.list()
    #
    #     plugin = event.arguments[2]
    #     action = event.arguments[1]
    #
    #     if plugin in plugins:
    #         if action == "enable":
    #             if plugins[plugin]['status'] == "Disabled":
    #                 self.core.plugin.load(plugin)
    #                 self.say(event.channel_id, f"Enabled plugin: **{plugin}**")
    #             else:
    #                 self.say(event.channel_id, f"{plugin} is already enabled")
    #
    #         elif action == "disable":
    #             if plugins[plugin]['status'] == "Enabled":
    #                 self.core.plugin.unload(plugin)
    #                 self.say(event.channel_id, f"Disabled plugin: **{plugin}**")
    #             else:
    #                 self.say(event.channel_id, f"{plugin} is already disabled")
    #     else:
    #         self.say(event.channel_id, "I don't have a plugin by that name.")
    #
    #
    @command("^uptime$")
    def uptime(self, event):
        """
            Description: Show how long bot has been connected
            Usage: arcbot uptime
        """
        uptime = time.time() - self.bot.backend.login_time

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
