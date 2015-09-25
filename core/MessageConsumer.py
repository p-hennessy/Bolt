"""
    Class Name : MessageConsumer

    Description:
        Daemon thread that is responsible for dispatching the message recieve event
        as well as invoking registered commands that match incoming messages

    Contributors:
        - Patrick Hennessy

    License:
        CL4M-B0T is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import threading
import re
import datetime

from core.Message import *

class MessageConsumer(threading.Thread):
    def __init__(self, core):
        super(MessageConsumer, self).__init__(name="MessageConsumer")
        self.core = core
        self.stopped = threading.Event()

        self.core.event.register("recieve.message")

    def run(self):
        self.stopped.clear()

        while True:
            message = self.core.connection.recieve()

            if(message):
                if(isinstance(message, Message.text)):
                    if message.sender in self.core.users:
                        message.sender = self.core.users[message.sender]

                    for server in self.core.servers:
                        channel = server.getChannel(message.channel)
                        if(channel):
                            message.channel = channel
                            message.server = server

                    print datetime.datetime.strptime(message.timestamp.split(".")[0], "%Y-%m-%dT%H:%M:%S").strftime("%s")
                    print message.sender
                    print message.channel
                    print message.server
                    print message.text


    def stop(self):
        self.stopped.set()
