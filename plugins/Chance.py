"""
    Description:
        Roll dice
        Flip coins
        Get random numbers
        Magic 8 ball ooo

    Contributors:
        - Patrick Hennessy
"""
from arcbot import Plugin
from arcbot import command
import random

class Chance(Plugin):
    @command("^roll( dice)?$")
    def roll(self, event):
        self.say(event.channel_id, f":game_die: Rolled a {random.randint(1,12)}")

    @command('^flip( coin)?$')
    def flip(self, event):
        output = random.randint(0,1)

        if output == 0:
            self.say(event.channel_id, "Heads")
        else:
            self.say(event.channel_id, "Tails")

    @command("^rand(om)?( number| num)?( between| from)? ([0-9]+) (to|and) ([0-9]+)")
    def random_number(self, event):
        args = event.arguments
        rand_num = random.randint(int(args[4]), int(args[6]))

        self.say(event.channel_id, f":hash: **Random Number**: {rand_num}")

    @command("^((O|o)h )?(M|m)agic (8|eight) ball(,|;) .+?$", trigger='')
    def magic_eight_ball(self, event):
        responses = [
            "Yes",
            "No",
            "No doubt",
            "Doubtful",
            "That is obviously true",
            "For sure",
            "No body knows for sure; but I'd bet on yes",
            "Does a bear crap in the woods?",
            "A birdie told me no",
            "Doesn't look good, sorry",
            "I see no reason why not",
            "Without a doubt",
            "Yeah right",
            "There is no doubt in my mind",
            "Probably",
            "Who knows?",
            "You know you're asking this to a robot?",
            "Seriously? You can ask anything in the world and thats what you ask? Smh",
            "I wouldn't place bets on it",
            "It has a high likely hood",
            "No chance in hell",
            "The magic 8 ball overlords don't want me to tell.",
            "You will have to wait, but yes",
            "Yeppers mcpeppers",
            "Absolutely"
        ]
        self.say(event.channel_id, f":8ball: {random.choice(responses)}")
