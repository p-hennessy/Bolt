"""
    Description:
        Roll dice
        Flip coins
        Get random numbers
        Magic 8 ball ooo

    Contributors:
        - Patrick Hennessy
"""
from bolt import Plugin
from bolt import regex_command
import random

class Chance(Plugin):
    @regex_command("^roll( dice)?$")
    def roll(self, event):
        self.say(event.message.channel_id, f":game_die: Rolled a {random.randint(1,12)}")

    @regex_command('^flip( coin)?$')
    def flip(self, event):
        output = random.randint(0,1)

        if output == 0:
            self.say(event.message.channel_id, "Heads")
        else:
            self.say(event.message.channel_id, "Tails")

    @regex_command("^(rand|roll) ([0-9]+) ([0-9]+)")
    def random_number(self, event):
        args, kwargs = event.arguments
        rand_num = random.randint(int(args[1]), int(args[2]))

        self.say(event.message.channel_id, f":game_die: Rolled a {rand_num}")
