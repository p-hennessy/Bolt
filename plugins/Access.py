"""
    Description:
        Implments a naive ACL system to prevent certain users from accessing bot commands

    Contributors:
        - Patrick Hennessy
"""
from arcbot import Plugin
from arcbot import command, pre_command_hook
from arcbot.utils import Timer
from arcbot.utils import Colors

class Access(Plugin):
    def activate(self):
        self.users = self.database.acl_users

    @pre_command_hook()
    def check_access(self, command, event):
        author = self.users.find_one({"id": event.author.id})

        if not author:
            author = {'access': 0}

        if not int(author['access']) >= int(command.access):
            if command.trigger is not None:
                self.say(event.channel_id, ":warning: You don't have enough access for that command.")
            return False

    @command("^set access ([0-9]+) ([0-9]+)$", access=999)
    def set_access(self, event):
        user_id = event.arguments[1]
        access = int(event.arguments[2])

        target_user = self.bot.api.get_user(user_id)
        target_user['access'] = access

        self.users.replace_one({"id": target_user['id']}, target_user, upsert=True)

        user = f"{target_user['username']}#{target_user['discriminator']}"
        self.say(event.channel_id, f"Set access for **{user}** to **{access}**")

    @command("^whois <@!?([0-9]+)>$")
    def whois(self, event):
        with Timer() as timer:
            embed = self.user_card(event.arguments[1])
            embed['footer'] = {"text": f"⏰ {timer.delta}ms | 🔌 ACL.whois"}
            self.say(event.channel_id, embed=embed)

    @command("^whoami$")
    def whoami(self, event):
        with Timer() as timer:
            embed = self.user_card(event.author.id)
            embed['footer'] = {"text": f"⏰ {timer.delta}ms | 🔌 ACL.whoami"}
            self.say(event.channel_id, embed=embed)

    def user_card(self, user_id):
        user = self.users.find_one({"id": user_id})

        if not user:
            user = self.bot.api.get_user(user_id)
            user['access'] = 0

        embed = {
            "title": f"{user['username']}",
            "description": "͢\n",
            "thumbnail": {
                "url": f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png"
            },
            "color": Colors.INFO,
            "fields": [
                {
                    "name": "ID",
                    "value": f"{user['id']}",
                    "inline": True
                },
                {
                    "name": "Access",
                    "value": f"{user['access']}",
                    "inline": True
                }
            ]
        }
        return embed
