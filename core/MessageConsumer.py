from core.Command import *
import threading
import time
import re

class MessageConsumer(threading.Thread):
    def __init__(self, core):
        super(MessageConsumer, self).__init__(name="MessageConsumer")
        self.core = core
        self.stopped = threading.Event()

        self.core.event.register("recieve.message")

    def run(self):
        self.stopped.clear()

        while not self.stopped.isSet():
            message = self.core.connection.recieve()

            if(message):
                self.core.event.notify("recieve.message", message=message)

                for command in self.core.command.matchCommands(message.text):
                    message.sender = self.core.user.getUser(message.sender)
                    message.channel = self.core.channel.getChannel(message.channel)

                    if(message.sender.getAccess() >= command.getAccess()):
                        command.invoke(message)

            message = None

    def stop(self):
        self.stopped.set()
