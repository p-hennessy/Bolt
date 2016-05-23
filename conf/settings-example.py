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
    avatar = None

    # Default command trigger. Messages that being with this are considered commands
    trigger = "arcbot "

    # Log level: https://docs.python.org/3/library/logging.html#logging-levels
    loglevel = logging.INFO

    # Connector to use
    connector = "Discord"
    connector_options = {
        "token": ""
    }

    # Ranks
    ranks = {
        "guest": 50,
        "member": 100,
        "moderator": 150,
        "admin": 999
    }

    # Names of plugins to be loaded. Will search the "plugin/" directory
    plugins = [
        "ACL",
        "Manage",
    ]

    # Thread Pool Execution
    #   worker_threads - number of worker threads to be spawned that will carry out tasks for the bot
    #   worker_queue_size - size of queue for thread workers to consume from. Big size = more tasks can be queued; but more RAM used
    worker_threads = 12
    worker_queue_size = 100

    # Watch Dog settings
    #   connection_retry - number of times watchdog will try to reconnect the bot
    #   connection_timeout - time in seconds to wait before trying to connect again
    connection_retry = 3
    connection_timeout = 900
