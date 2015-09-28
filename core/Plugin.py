"""
    Class Name : Plugin

    Description:
        Superclass for which all plugins are derived

    Contributors:
        - Patrick Hennessy

    License:
        CL4M-B0T is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import logging

class Plugin(object):
    def __init__(self, core, name):
        self.core = core
        self.name = name

        self.logger = logging.getLogger("plugins." + self.name)

    def activate(self):
        pass

    def deactivate(self):
        pass

    # Exposed methods for Plugin use
    def reply(self, envelope, message):
        self.core.connection.reply(envelope, message)

    def say(self, channel, message):
        self.core.connection.send(channel, message)

    def whisper(self, user, message):
        pass
