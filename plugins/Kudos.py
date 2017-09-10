"""
    Description:
        Allows users to give Kudos to things

    Contributors:
        - Patrick Hennessy
"""
from arcbot import Plugin
from arcbot import command
from arcbot.utils import Timer

class Kudos(Plugin):
    def activate(self):
        self.kudos = self.database.kudos

    @command("^top kudos")
    def top(self, event):
        with Timer() as timer:
            top = self.kudos.find(sort=[("count", -1)], limit=5)
            output = "Top 5 kudos are:```"

            names = ""
            points = ""

            for item in top:
                name = item['key']
                count = item['count']

                names += f"{name}\n"
                points += f"{count}\n"

            embed = {
                "fields": [
                    {
                        "name": "Name",
                        "value": names,
                        "inline": True
                    },
                    {
                        "name": "Points",
                        "value": points,
                        "inline": True
                    }
                ],
                "footer": {
                    "text": f"⏰ {timer.delta}ms | 🔌 Kudos.top"
                }
            }

            self.say(event.channel_id, "**Top 5 Kudos**: ", embed=embed)

    @command("^who the man?", access=1000)
    def who_the_man(self, event):
        self.say(event.channel_id, "You the man!", mentions=[event.author.id])

    @command("(.*)\+\+$", trigger=None)
    def plus_kudos(self, event):
        target = event.arguments[1].lower()

        self.kudos.update_one({"key": target}, {'$inc': {'count': 1}}, upsert=True)
        points = self.kudos.find_one({"key": target})["count"]

        self.say(event.channel_id, f"**{target}** has {points} points")

    @command("(.*)\-\-$", trigger=None)
    def minus_kudos(self, event):
        target = event.arguments[1].lower()

        self.kudos.update_one({"key": target}, {'$inc': {'count': -1}}, upsert=True)
        points = self.kudos.find_one({"key": target})["count"]

        self.say(event.channel_id, f"**{target}** has {points} points")
