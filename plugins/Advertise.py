"""
    Description:
        Gives basic commands to the bot

    Contributors:
        - Patrick Hennessy
"""
from arcbot import Plugin
from arcbot import command, interval

import random

class Advertise(Plugin):
    def activate(self):
        self.ads = self.database.ads
        self.ad_channels = self.database.ad_channels

    @command("^add ad ([^\ ]+) (.+)$")
    def add_ad(self, event):
        category = event.arguments[1]
        text = event.arguments[2]

        new_ad = {"category": category, "text": text}

        self.ads.insert_one(new_ad)
        self.say(event.channel_id, f"Added new ad to **{category}** category")

    @command("^advertise in ([0-9]+) (.+)$")
    def set_add_channel(self, event):
        channel_id = event.arguments[1]
        categories = event.arguments[2]

        new_ad_channel = {
            "channel_id": channel_id,
            "categories": [category for category in categories.split(" ")]
        }

        self.ad_channels.replace_one({"channel_id": channel_id}, new_ad_channel, upsert=True)
        self.say(event.channel_id, f"Channel {channel_id} advertising: `{categories}`")

    @command("^stop ads in ([0-9]+)$")
    def remove_add_channel(self, event):
        channel_id = event.arguments[1]

        self.ad_channels.delete_one({"channel_id": channel_id})
        self.say(event.channel_id, f"Stopping all ads in `{channel_id}`")

    @interval(60*60)
    def advertise(self):
        for channel in self.ad_channels.find():
            channel_id = channel['channel_id']
            category = random.choice(channel['categories'])

            pipeline = [
                {"$match": {"category": category}},
                {"$sample": {"size": 1}}
            ]
            ad = list(self.ads.aggregate(pipeline))[0]["text"]

            last_message = self.bot.api.get_channel_messages(channel_id, limit=1)

            if last_message[0]['author']['id'] != "168419936966934528":
                category = category.replace("_", " ")
                category = category.title()

                self.say(channel_id, f":mega: **{category}**: {ad}")
