"""
    Class Name : User

    Description:
        Provides staging area for user data

    Contributors:
        - Patrick Hennessy

    License:
        PhilBot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

class User():
    def __init__(self, id, username, isAdmin=False, realName=None, email=None):
        self.id = id
        self.username = username
        self.realName = realName
        self.email = email
        self.isAdmin = False
        self._access = 0

    def setAccess(self, access):
        self._access = access

    def getAccess(self):
        return self._access

    def getPreferedName(self):
        if(self.realName != None and len(self.realName) > 0):
            return self.realName
        else:
            return self.username

class UserManager():
    def __init__(self, core, users=[]):
        self.core = core
        self.users = users

    def addUser(self, user):
        self.users.append(user)

    def removeUser(self, uid):
        for user in self.users:
            if(user.id == uid):
                self.users.remove(user)

    def updateUserList(self):
        self.users = self.core.connection.getUsers()

    def getUserList(self):
        self.updateUserList()

        return self.users

    def getUser(self, uid):
        for user in self.users:
            if(user.id == uid):
                return user

        newUser = self.core.connection.getUser(uid)
        self.addUser(newUser)

        return newUser

    def getUsername(self, uid):
        return self.getUser(uid).getPreferedName()
