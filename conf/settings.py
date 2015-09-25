import logging

class Config():

    name = "CL4M-B0T"
    trigger = "."
    loglevel = logging.DEBUG

    connector = "discord"
    connectorOptions = {
        "email": "pmh35480@gmail.com",
        "password": "clambotpassword"
    }

    plugins = [
        "Chat",
    ]
