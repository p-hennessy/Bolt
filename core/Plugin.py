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
from core.Database import *

from typing import List, Dict

class Plugin(object):
    def __init__(self, core, name: str):
        self.core = core
        self.name = name
        self.database = Database(databaseName=f"databases/{self.name}.db")

        self.logger = logging.getLogger(f"plugins.{self.name}")


    def activate(self) -> None:
        pass


    def deactivate(self) -> None:
        pass


    def reply(self, envelope: tuple, message: str) -> None:
        self.core.connection.reply(envelope.sender, envelope.channel, message)


    def say(self, channel: str, message: str, embed: Dict = {}, mentions: List = []) -> None:
        self.core.connection.say(channel, message, mentions=mentions)


    def whisper(self, user: str, message: str) -> None:
        self.core.connection.whisper(user, message)


    def upload(self, channel: str, file: str) -> None:
        self.core.connection.upload(channel, file)
