"""
    Class Name : Plugin

    Description:
        Superclass for which all plugins are derived

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import logging
from arcbot.Database import *

from typing import List, Dict

class Plugin(object):
    def __init__(self, core, name: str):
        self.core = core
        self.name = name
        self.database = Database(databaseName=f"databases/{self.name}.db")

        self.logger = logging.getLogger(f"plugins.{self.name}")

    def activate(self):
        pass

    def deactivate(self):
        pass

    def say(self, channel_id, message="", embed={}, mentions=[]):
        self.core.connection.say(channel_id, message=message, embed=embed, mentions=mentions)

    def whisper(self, user_id, message="", embed={}, mentions=[]):
        self.core.connection.whisper(user_id, message=message, embed=embed, mentions=mentions)

    def upload(self, channel, file):
        self.core.connection.upload(channel, file)
