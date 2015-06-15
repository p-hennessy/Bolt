#!/usr/bin/python

from lib.SlackClient import *
from lib.Timer import *

import time
import random
import re
import inspect
        
def main():        
        
    Regis = Trivia()
    
    Regis.login("xoxb-6375106610-BkKQoLIxFIX1NacVr4FGSEEj")
    Regis.say("Regis Philbot 2.0 Initializing...")
    Regis.start()
    
    Regis.logout()

class Bot():  
    def __init__(self):
        self.connection = None
        self.userInfo = {}
        
    def login(self, token):
        self.connection = SlackConnection(token)
        self.userInfo = self.connection.getBotData()

    def logout(self):
        self.connection.disconnect()
    
    def say(self, message, channel="general"):
        self.connection.emit(channel, message)
        
    def listen(self):
        return self.connection.recv()
    
    def parseMessage(self, messageData):    
        if("type" in messageData.keys() and messageData["type"] == "message"): 
            sender = messageData["user"]
            message = messageData["text"]

            # Don't care about own messages
            if(sender == self.userInfo["id"]):
                return

            # If message is a command
            elif(re.match(r"^regis\ ", message)):
                self.parseCommand(re.sub(r"^regis\ ", "", message))
            
            else:
                return messageData
                
    def parseCommand(self, command):
        args = command.split(" ")
        
        try:
            commandInvocation = getattr(self, args[0])
        except AttributeError:
            return
                
        try:
            commandInvocation(*args[1:])
        except TypeError:
            #self.say("[Command Error]: " + commandInvocation.__doc__ + " " + str(len(args[1:])) + " were given.")
            return
            
        
class Trivia(Bot):
    def __init__(self):
        self.timer = Timer()
        self.questions = None
        self.running = False
    
    def start(self):
        if not self.running:
            self.running = True
            
        while self.running:
            
            # Random Pause
            self.wait(10)
            
            # Ask Question
            self.say("Heres a question!")
            
            # Listen for answer, giving hint
            for i in range(0, 2):
                answer = self.wait(15, True)

                # If found...
                if(answer):
                    username = self.connection.getUserData(answer["user"])["user"]["name"]
                                        
                    self.say("Correct! " + username + ", you earned $10!")
                    self.say("Your riches have amassed to a staggering $30!")
                    
                    break

                # Give a hint
                else:
                    self.say("Giving hint...")
          
        
        
    def wait(self, seconds, checking=False):
        self.timer.start()
        
        while( self.timer.getElapsedTime() < seconds ):
            line = self.listen()
            
            if(line):
                message = self.parseMessage(line)

                if(self._checkAnswer(message) and checking):
                    return message                
                

    def stop(self):        
        """ Trivia.stop() | Stops playing trivia. Takes 0 arguments. """
        self.running = False
    
    def _askQuestion(self, question):
        pass
    
    def _checkAnswer(self, question):
        if(question and question["text"] == "test"):
            return True
        else:
            return False

    
    
    

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.exit(1)