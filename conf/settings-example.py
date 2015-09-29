"""
    Class Name : Config

    Description:
        Contains all global config options needed for the bot to run

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import logging

class Config():

    # Name the bot will refer to itself; will change name on server if it is not this
    name = "Arcbot"

    # Default command trigger. Messages that being with this are considered commands
    trigger = "."

    # Log level: https://docs.python.org/2/library/logging.html#logging-levels
    loglevel = logging.INFO

    # Connector to use
    connector = "Discord"
    connectorOptions = {
        "email": "",
        "password": ""
    }

    # Names of plugins to be loaded. Will search the "plugin/" directory
    plugins = [
        "Manage",
    ]

    # ACL
    ranks = {
        "owner": 1000,
        "admin": 999,
        "member": 100,
        "guest": 10,
    }

    # Thread Pool Execution
    #   threadedWorkers - number of worker threads to be spawned that will carry out tasks for the bot
    #   threadPoolQueueSize - size of queue for thread workers to consume from. Big size = more tasks can be queued; but more RAM used

    threadedWorkers = 3
    threadPoolQueueSize = 25
