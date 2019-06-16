"""
    Description:
        Commands related to basic managment

    Contributors:
        - Patrick Hennessy
"""
from bolt import Plugin
from bolt import command, regex_command, parse_command, interval, subscriber
from bolt.utils import Colors, Timer, readable_time
from bolt.discord import Events

from base64 import b64encode
import time
from datetime import datetime

class Manage(Plugin):
    @command("ping")
    def ping(self, event):
        self.say(event.message.channel_id, f":satellite: **{self.bot.websocket.ping}**ms")

    @command("trigger", trigger="?")
    def trigger(self, event):
        self.say(event.message.channel_id, f"My default trigger is `{self.bot.config.trigger}`")

    @command("cron")
    def cron(self, event):
        callbacks = ""
        nexts = ""

        for plugin in self.bot.plugins:
            if plugin.enabled:
                for cron in plugin.crons:
                    next = datetime.fromtimestamp(cron.cron.get_current())

                    callbacks += f"{cron.callback.__qualname__}\n"
                    nexts += f"{next}\n"

        embed = {
            "color": Colors.INFO,
            'fields': [
                {'name': 'Handler', 'value': callbacks, "inline": True},
                {'name': 'Next', 'value': nexts, "inline": True}
            ]
        }

        self.say(event.message.channel_id, embed=embed)

    @command("uptime")
    def uptime(self, event):
        elapsed = time.time() - self.bot.websocket.login_time
        self.say(event.message.channel_id, f"I've been connected for: **{readable_time(elapsed)}**")

    @command("invite")
    def invite(self, event):
        embed = {
            "description": ":sunglasses: [**Click to invite me to your server!**](https://discordapp.com/oauth2/authorize?client_id=399458284769378309&scope=bot&permissions=85056)"
        }
        self.say(event.message.channel_id, embed=embed)

    @command("list plugins")
    def list_plugins(self, event):
        plugins = self.bot.plugins

        names = "".join([type(plugin).__name__ + "\n" for plugin in plugins])
        statuses = "".join(["Enabled\n" if plugin.enabled else "Disabled\n" for plugin in plugins])

        embed = {
            "color": Colors.INFO,
            'fields': [
                {'name': 'Name', 'value': names, "inline": True},
                {'name': 'Status', 'value': statuses, "inline": True}
            ]
        }
        self.say(event.message.channel_id, embed=embed)

    # def set_name(self):
    #     with open("avatar.png", "rb") as file:
    #         raw = file.read()
    #         data = b64encode(raw).decode('ascii')
    #
    #     avatar_data = f"data:image/png;base64,{data}"
    #     self.bot.api.modify_current_user(username=self.bot.config.name, avatar_data=avatar_data)
