"""
    Class Name : MessageParser

    Description:
        Provides an extensible engine for plugins to interact with
        Features:
            - Publish / Subscribe Event System
            - Plugin manager
            - Configuration manager
            - User, Channel and Group Date manager

    Contributors:
        - Patrick Hennessy

    License:
        PhilBot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

"""
    pressence_change
    hello
    user_typing


"""

import json
import threading

class MessageParser(threading.Thread):
    def __init__(self, core):
        super(MessageParser, self).__init__(name="MessageParser")
        self.core = core

        self.core.event.register("recieve.message")
        self.core.event.register("recieve.command")

    def run(self):
        while self.core.connection.connected:
            messageBuffer = self.core.connection.consumeMessageBuffer()

            if(messageBuffer):
                for message in messageBuffer:
                    if not("type" in message.keys()):
                        continue

                    if(message["type"] == "message"):
                        self.core.command.invoke(message["text"])
                        self.core.event.publish("recieve.command", text=message["text"], uid=message["user"], timestamp=message["ts"], channel=message["channel"])
