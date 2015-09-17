import threading
import datetime

from lib.Command import *

def init(bot):
    chatThread = Chat(bot)
    chatThread.start()

    return chatThread

def destroy():
    pass

class Chat(threading.Thread):
    def __init__(self, bot):
        super(Chat, self).__init__()
        self.bot = bot

        self.bot.subscribe("recieve.message", self.onMessage)
        self.bot.subscribe("recieve.command", self.onMessage)

        self.bot.registerCommand( Command("ping", self.ping) )

    def run(self):
        pass

    # Commands
    def ping(self, *args):
        self.bot.say("Pong!")

    # Event Handlers
    def onMessage(self, args):

        timestamp = datetime.datetime.fromtimestamp( float(args["timestamp"]) ).strftime('%m/%d/%Y %H:%M:%S')
        username = self.bot.getUserInfo(args["uid"])["user"]["name"]

        print "[" + timestamp + "] <" + username + "> "+ args["text"]
