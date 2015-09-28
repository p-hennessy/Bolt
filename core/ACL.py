"""
    Class Name : ACL

    Description:

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

"""
    uid{
        "globalAccess": globalAccess,
        "commandWhitelist": []
    }

    ACL INTERFACE?
    .acl ranks                      List ranks available
    .acl add [user] [rank|access]   Add user pat as admin user
    .acl get [user]                 Get ACL data about pat
    .acl set [user] [rank|access]   Set user pat rank or access
    .acl grant [user] [command]     Add to command whitelist
    .acl revoke [user] [command]    Remove from command whitelist
"""

from core.Database import Database

class ACL():
    def __init__(self):
        self.userList = {}
        self.database = Database("acl")

    def loadACL(self):
        pass

    def addUser(self, uid, globalAccess=0, commandAccess={}):
        user = {
            "globalAccess": globalAccess,
            "commandAccess": commandAccess
        }

        if not(self.database.hasKey(uid)):
            self.database.set(uid, user)
            self.userList["uid"] = user

    def updateUser(self, uid, globalAccess=None, commandAccess=None):
        pass

    def deleteUser(self, uid):
        pass

    def getUser(self, uid, access):
        if(uid in self.userList):
            return self.userList[uid]

        elif(self.database.hasKey(uid)):
            user = self.database.get(uid)
            self.userList[uid] = user

            return user
        else:
            return None
