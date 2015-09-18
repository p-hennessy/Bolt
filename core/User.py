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

import collections
import functools
import time

class User():
    def __init__(self, id, username, isAdmin=False, isOwner=False, realName=None, email=None, phone=None):
        self.id = id
        self.username = username
        self.realName = realName
        self.email = email
        self.phone = phone
        self.isAdmin = False
        self.isOwner = False
        self.access = 0

    def grantAccess(self, access):
        self.access = access

    def isAdmin(self):
        return self.isAdmin

    def isOwner(self):
        return self.isOwner

    def getPreferedName(self):
        if(self.realName != None and len(self.realName) > 0):
            return self.realName
        else:
            return self.username

class UserManager():
    def __init__(self, core):
        self.core = core
        self.users = []

        # Get an initial list of users
        userList = self.core.connection.slackAPI.users.list(self.core.botConfig["authToken"])

        for user in userList["members"]:
            self.addUser(user)

    def addUser(self, userData):
        newUser = User(
            userData["id"],
            userData["name"],
            userData["is_admin"],
            userData["is_owner"],
            userData["profile"]["real_name"]
        )

        self.users.append(newUser)
        return newUser

    def getUID(self, username):
        for user in self.users:
            if(user.username == username):
                return user.id

        return None

    def getUsername(self, uid):
        # Check if user is in our list
        for user in self.users:
            if(user.id == uid):
                return str(user.getPreferedName())

        # If not, we must get their info and add them
        newUser = self.addUser(self.getUserInfo(uid)["user"])
        if not newUser:
            return uid

    def getUserInfo(self, uid):
        return self.core.connection.slackAPI.users.info(self.core.botConfig["authToken"], uid)
