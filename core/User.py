"""
    Class Name : User

    Description:
        Provides staging area for user data

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

class User():
    def __init__(self, id, username, isAdmin=False, email=None):
        self.id = id
        self.username = username
        self.email = email
        self.isAdmin = False
        self._access = 0

    def __call__(self):
        return self.id

    def __str__(self):
        return self.getName()

    def setAccess(self, access):
        self._access = access

    def getAccess(self):
        return self._access

    def getName(self):
        return self.username
