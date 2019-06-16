"""
    Description:
        Posts in a channel when getting webhooks from Github

    Contributors:
        - Patrick Hennessy
"""
from bolt import Plugin
from bolt import command

class Github(Plugin):
    @command("^(github|source code|repo|code)$")
    def repo(self, event):
        self.say(event.channel_id, "You can find my code at: https://github.com/scrims-tf/discord-bot-plugins")
