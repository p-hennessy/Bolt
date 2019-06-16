"""
    Description:
        Allows you to lookup Urban Dictionary definitions

    Contributors:
        - Patrick Hennessy
"""
from bolt import Plugin
from bolt import regex_command
from bolt.utils import Colors

import requests

class UrbanDictionary(Plugin):
    @regex_command("^define (.*)$")
    def define(self, event):
        args, kwargs = event.arguments
        query = args[0].replace(" ", "+")
        url = f"https://api.urbandictionary.com/v0/define?term={query}"
        response = requests.get(url)
        raw = response.json()

        if not response.status_code == 200:
            self.say(event.message.channel_id, "Great job, you broke UrbanDictionary")
            return

        defintions = response.json().get('list')

        if not defintions:
            self.say(event.message.channel_id, "Couldn't find a urban definition for that.")
            return

        definition = defintions[0]['definition']
        example = defintions[0]['example']
        permalink = defintions[0]['permalink']
        word = defintions[0]['word']

        if len(definition + example) > 1800:
            self.say(event.message.channel_id, "Definition was too long, check it out yourself: {}".format(permalink))
            return

        embed = {
            "title": f":book: {word}",
            "url": permalink,
            "fields": [
                {
                    "name": "Definition",
                    "value": definition
                },
                {
                    "name": "Example",
                    "value": example
                }
            ]
        }

        self.say(event.message.channel_id, embed=embed)
