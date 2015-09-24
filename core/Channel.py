"""
    Class Name : Channel

    Description:
        Provides staging area for channel data

    Contributors:
        - Patrick Hennessy

    License:
        PhilBot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

class Channel():
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def getName(self):
        return self.name

    def getID(self):
        return self.id
