"""
    Plugin Name : ACL
    Plugin Version : 1.0

    Description:
        Gives basic commands to the bot

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation

    .acl ranks                      List ranks available
    .acl add [user] [rank|access]   Add user pat as admin user
    .acl get [user]                 Get ACL data about pat
    .acl set [user] [rank|access]   Set user pat rank or access
    .acl grant [user] [command]     Add to command whitelist
    .acl revoke [user] [command]    Remove from command whitelist
"""

from core.Plugin import Plugin
from core.Decorators import *
from peewee import *

import random
import string

class ACL(Plugin):

    def activate(self):
        self.ownerUser = self.checkOwner()

    @command('^claim [A-Za-z0-9]')
    def claim(self, msg):
        if(msg.content.split(' ')[1] == self.key):
            self.logger.critical('Bot has been claimed by: {}'.format(msg.sender))

            with self.database.lock:
                ownerUser, created = self.database.User.create_or_get(id=msg.sender)
                ownerUser.name = self.core.connection.getUser(msg.sender)['name']
                ownerUser.access = 1000
                ownerUser.owner = True
                ownerUser.save()
                self.ownerUser = ownerUser

            self.reply(msg, 'You are now my owner! Wooo')

    @command('^owner')
    def owner(self, msg):
        self.say(msg.channel, 'My owner is: *{}*'.format(self.ownerUser.name))

    @command('^acl (ranks|add|get|set|grant|revoke)')
    def acl(self, msg):
        pass

    def checkOwner(self):
        # Check for owner
        with self.database.lock:
            ownerQuery = self.database.User.select().where( self.database.User.owner == True )

        for user in ownerQuery:
            return user

        # If we don't find an owner
        self.key = self.generateKey(16)
        self.logger.critical('Claim bot in chat using this command: .claim {}'.format(self.key))
        return None

    def generateKey(self, length):
        return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))
