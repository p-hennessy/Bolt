"""
    Plugin Name : ACL
    Plugin Version : 1.0

    Description:
        Allows a chat interface to modifying user access

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *
from peewee import *

import random
import string

ACCESS = {
    "claim": -1,
    "deleteAccess": -1,
    "setAccess": -1
}

class ACL(Plugin):

    def activate(self):
        if not self.core.ACL.getOwner():
            self.key = self.generateKey(32)
            self.logger.warning("Claim this bot by typing 'arcbot claim {}'".format(self.key))

    @command('^claim [A-Za-z0-9]', access=ACCESS["claim"])
    def claim(self, msg):
        if(msg.content.split(' ')[1] == self.key):
            self.logger.critical('Bot has been claimed by: {} UID:{}'.format(msg.senderNickname, msg.sender))
            self.core.ACL.setOwner(msg.sender)
            self.reply(msg, 'You are now my owner! Wooo')

    @command("^access delete <@([0-9]+)>", access=ACCESS["deleteAccess"])
    def deleteAccess(self, msg):
        requestor = msg.sender
        target = msg.getMatches()[0]

        if(requestor == target):
            self.reply(msg, "You cannot modify your own access")
            return

        # Check if requestor is allowed to do this
        if(self.core.ACL.getAccess(requestor) >= self.core.ACL.getAccess(target)):
                print(self.core.ACL.deleteUser(target))
                self.say(msg.channel, "Removed UID:`{}` from access list".format(target))
        else:
            self.reply(msg, "You cannot modify access of a user with more access")

    @command("^access set <@([0-9]+)> ([0-9]+)", access=ACCESS["setAccess"])
    def setAccess(self, msg):
        requestor = msg.sender
        target = msg.getMatches()[0]

        # Check if requestor is allowed to do this
        if(requestor == target):
            self.reply(msg, "You cannot modify your own access")
            return

        if(self.core.ACL.getAccess(requestor) >= self.core.ACL.getAccess(target)):
            access = int(msg.getMatches()[1])
            if(access >= 0 and access < 1000):
                self.core.ACL.setAccess(target, access)
                self.say(msg.channel, "Set UID:`{}` to access level: `{}`".format(target, access))
            else:
                self.reply(msg, "Access must be between 0 and 999")

        else:
            self.reply(msg, "You cannot modify access of a user with more access")

    def generateKey(self, length):
        return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))
