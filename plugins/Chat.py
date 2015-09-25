"""
    Plugin Name : Chat
    Plugin Version : 1.0

    Description:
        Gives basic commands to the bot

    Contributors:
        - Patrick Hennessy

    License:
        CL4M-B0T is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *

class Chat(Plugin):

    def activate(self):
        pass

    @command("^ping$")
    def ping(self, msg):
        pass

    @subscriber("connection.login")
    def uptime(self, *args, **kwargs):
        print args
        print kwargs
