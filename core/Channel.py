"""
    Class Name : Channel

    Description:
        Provides staging area for user data

    Contributors:
        - Patrick Hennessy

    License:
        PhilBot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

class Channel():
    def __init__(self, id, name, created=0, creator=None, archived=False):
        self.id = id
        self.name = name
        self.created = created
        self.creator = creator
        self.archived = archived
