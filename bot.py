#!/usr/bin/python

from lib.SlackClient import *
import time

class Bot():
    
    def __init__(self):
        self.socket = None
        self.userData = {}
        
    def login(self, token):
        self.socket = SlackConnection(token)
        self.userData = self.socket.getUserData()
        
        self.say("Regis Philbot 2.0 Initializing...")
    
    def logout(self):
        self.socket.disconnect()
    
    def join(self, channel):
        pass
    
    def whisper(self, message, user):
        pass
    
    def say(self, message, channel="general"):
        self.socket.emit(channel, message)
        
    def listen(self):
        return self.socket.recv()
            

bot = Bot()
bot.login("xoxb-6375106610-BkKQoLIxFIX1NacVr4FGSEEj")

time.sleep(1)

while True:
    message = bot.listen()
    
    if(message):
        print message

