#! /usr/bin/python3

"""
    Class Name : Main

    Description:
        Entry point for loading Arcbot

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""
from core.Core import Bot
from connectors.Discord import Discord

arcbot = Bot()
arcbot.trigger = 'arcbot '
arcbot.connector = Discord(arcbot, token="")

for plugin in arcbot.discover_plugins('plugins'):
    arcbot.plugin.load(plugin)

arcbot.connect()
