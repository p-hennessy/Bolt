"""
    Description:
        Get some much needed inspiration

    Contributors:
        - Patrick Hennessy
"""
from bolt import Plugin
from bolt import regex_command
import requests

class Inspire(Plugin):
    @regex_command("^inspire(\ me)?$")
    def inspire(self, event):
        response = requests.get('http://inspirobot.me/api?generate=true')
        response.raise_for_status()
        self.say(event.message.channel_id, response.text)
