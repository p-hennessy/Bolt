#!/usr/bin/python

from lib.SlackClient import *

class Bot():
    
    def __init__(self):
        self.socket = None
        self.userData = {}
        
    def login(self, token):
        self.socket = SlackConnection(token)
        self.userData = self.socket.getUserData()
        
        print "ID: " + self.userData["id"]
        print "Name: " + self.userData["name"]
    
    def join(self, channel):
        pass
    
    def whisper(self, message, user):
        pass
    
    def say(self, message, channel="C06B11LBE"):
        self.socket.emit(channel, message)
            

bot = Bot()

bot.login("xoxb-6375106610-BkKQoLIxFIX1NacVr4FGSEEj")

bot.say("hello")
