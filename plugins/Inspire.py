"""
    Description:
        Get some much needed inspiration

    Contributors:
        - Patrick Hennessy
"""
from arcbot import Plugin
from arcbot import command
import requests

class Inspire(Plugin):
    @command("^inspire(\ me)?$")
    def inspire(self, event):
        response = requests.get('http://inspirobot.me/api?generate=true')
        response.raise_for_status()
        self.say(event.channel_id, response.text)
