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
from arcbot.Core import Bot
import sys

arcbot = Bot("TOKEN HERE")
arcbot.trigger = 'arcbot '

for plugin in arcbot.plugin.discover('plugins'):
    arcbot.plugin.load(plugin)

arcbot.connect()

try:
    arcbot.run_forever()
except KeyboardInterrupt:
    arcbot.disconnect()
    arcbot.exit()

    sys.exit(0)
