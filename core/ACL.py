"""
    Class Name : ACL

    Description:
        Class that handles Access Control Lists for bot users
        This class serves as a RESTful abstration to the user database

    Contributors:
        - Patrick Hennessy
        - Aleksandr Tihomirov

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from peewee import *
from core.Database import *

class ACLUser(Model):
    id      = IntegerField(primary_key=True)
    access  = IntegerField(default=0, constraints=[Check('access >= 0'), Check('access <= 1000') ])
    owner   = BooleanField(default=False)

class ACL():
    def __init__(self):
        self.database = Database(databaseName="databases/ACL.db")
        self.database.addTable(ACLUser)

    def getOwner(self):
        try:
            user = ACLUser.get(owner=True)
            return user.id
        except:
            return None

    def setOwner(self, uid):
        user, created = self.database.ACLUser.get_or_create(id=uid)

        if(created):
            user.id = uid
            user.access = 1000
            user.owner = True
            user.save()
        else:
            user.owner = True
            user.save()

    def setAccess(self, uid, access):
        # Check if trying to change owner
        if(self.getOwner == uid):
            return False

        # Set user access
        user, created = self.database.ACLUser.get_or_create(id=uid)

        if(created):
            user.id = uid
            user.access = access

            user.save()
        else:
            user.access = access
            user.save()

        return True

    def getAccess(self, uid):
        try:
            user = ACLUser.get(id=uid)
            return user.access
        except:
            return -1

    def deleteUser(self, uid):
        try:
            user = self.database.ACLUser.get(id=uid)
            if(user):
                user.delete_instance()
                return True
            else:
                return False
        except:
            return False
