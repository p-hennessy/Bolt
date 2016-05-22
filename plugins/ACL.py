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
from tabulate import tabulate

import random
import string

ACCESS = {
    "claim": -1,
    "deleteAccess": 150,
    "setAccess": 150
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

    @command("^whois <@([0-9]+)>", access=50)
    def whois(self, msg):
        target = msg.getMatches()[0]
        access = self.core.ACL.getAccess(target)

        self.say(msg.channel, "User ID\t`{}`\nAccess:\t`{}`".format(msg.sender, access))

    @command("^whoami", access=50)
    def whoami(self, msg):
        access = self.core.ACL.getAccess(msg.sender)

        self.reply(msg, "\nUser ID\t`{}`\nAccess:\t`{}`".format(msg.sender, access))

    @command('^list users ([0-9]+)( [0-9]+)?( [0-9]+)?', access=100)
    def getUsers(self, msg):
        access, limit, offset = msg.getMatches()

        table = []
        for user in self.core.ACL.getUsers(access, limit, offset):
            table.append([user.id, user.cname, user.access])

        output = "**Users in my database: **\n\n"
        output += "`{}`".format(tabulate(table, headers=["ID", "Name", "Access"], tablefmt="psql", numalign="left"))

        self.say(msg.channel, output)

    @command("^delete access <@([0-9]+)>", access=ACCESS["deleteAccess"])
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

    @command("^set access <@([0-9]+)> ([0-9]+)", access=ACCESS["setAccess"])
    def setAccess(self, msg):
        requestor = msg.sender
        target = msg.getMatches()[0]

        # Check if requestor is allowed to do this
        if(requestor == target):
            self.reply(msg, "You cannot modify your own access")
            return

        if(self.core.ACL.getAccess(requestor) > self.core.ACL.getAccess(target)):
            access = int(msg.getMatches()[1])
            if(access >= 0 and access < 1000):
                name = self.core.connection.getUser(target)["name"]

                self.core.ACL.setAccess(target, access, cname=name)
                self.say(msg.channel, "Set **{}** UID:`{}` to access level: `{}`".format(name, target, access))
            else:
                self.reply(msg, "Access must be between 0 and 999")

        else:
            self.reply(msg, "You cannot modify access of a user with more access")

    def generateKey(self, length):
        return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))
