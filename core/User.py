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
    def __init__(self, id, username, isAdmin=False, isOwner=False, realName=None, email=None, phone=None):
        self.id = id
        self.username = username
        self.realName = realName
        self.email = email
        self.phone = phone
        self.isAdmin = False
        self.isOwner = False

    def update(self, uid):
        pass

class UserManager():
    def __init__(self):
        pass

    def getInfo(self, uid):
        pass
