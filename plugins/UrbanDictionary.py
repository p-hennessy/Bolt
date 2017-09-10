"""
    Description:
        Allows you to lookup Urban Dictionary definitions

    Contributors:
        - Patrick Hennessy
"""
from arcbot import Plugin
from arcbot import command
from arcbot.utils import Timer
from arcbot.utils import Colors

import requests

class UrbanDictionary(Plugin):
    @command("^define (.*)$")
    def define(self, event):
        with Timer() as timer:
            query = event.arguments[1].replace(" ", "+")
            url = f"https://api.urbandictionary.com/v0/define?term={query}"
            response = requests.get(url)
            raw = response.json()

            if not response.status_code == 200:
                self.say(event.channel_id, "Great job, you broke UrbanDictionary")
                return

            defintions = response.json().get('list')

            if not defintions:
                self.say(event.channel_id, "Couldn't find a urban definition for that.")
                return

            definition = defintions[0]['definition']
            example = defintions[0]['example']
            permalink = defintions[0]['permalink']
            word = defintions[0]['word']

            if len(definition + example) > 1800:
                self.say(event.channel_id, "Definition was too long, check it out yourself: {}".format(permalink))
                return

            embed = {
                "title": f":book: {word}",
                "url": permalink,
                "thumbnail": {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/UD_logo-01.svg/250px-UD_logo-01.svg.png"},
                "description": "͢\n",
                "fields": [
                    {
                        "name": "Definition",
                        "value": definition
                    },
                    {
                        "name": "Example",
                        "value": example
                    }
                ],
                "footer": {"text": f"⏰ {timer.delta}ms | 🔌 UrbanDictionary.define"}
            }

            self.say(event.channel_id, embed=embed)
