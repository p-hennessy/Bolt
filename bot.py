#!/usr/bin/python

from lib.SlackClient import *
from lib.Timer import *

from select import select

import time
import random
import re
import sys

        
def main():        
        
    Regis = Trivia()
    
    Regis.login("xoxb-6375106610-PiKFtyOj00bOBqTbaqCskYBb")
    Regis.say("Regis Philbot 2.0 Initializing...")
    Regis.listen(100)
    
    Regis.logout()

class Bot():  
    def __init__(self):
        self.connection = None
        self.session = None
        
        self.userInfo = {}
        self.timer = Timer()
        
    def login(self, token):
        self.connection = SlackConnection(token)
        self.userInfo = self.connection.getBotData()

    def logout(self):
        self.connection.disconnect()
        sys.exit(0)
    
    def say(self, message, channel="general"):
        self.connection.emit(channel, message)
    
    def ping(self):
        print self.connection.ping()
        
    def listen(self, duration, onMessage=None):
        self.timer.start()
        
        if not onMessage:
            onMessage = getattr(self, "_onMessage")
        
        self.listening = True
        while(self.timer.getElapsedTime() < duration and self.listening):
            message = self.connection.recv()

            rlist, _, _ = select([sys.stdin], [], [], 0)
            if rlist:
                input = sys.stdin.readline()
                self.parseCommand(input)
            
            if(message):
                message = self.parseMessage(message)             
                
                if(message):
                    onMessage(message)
                    
        self.listening = False
     
    def _onMessage(self, message):
        print message
            
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
        args = []
        
        for arg in re.findall(r'(?:"[^"]*"|\'[^\']*\'|[^\s\'"])+', command):
            arg = re.sub(r'^["\']|["\']$', '', arg)
            args.append(arg)
            
        print args
            
        try:
            commandInvocation = getattr(self, args[0])
            commandInvocation(*args[1:])
        except AttributeError:
            return
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
            # Ask Question
            self.say("Heres a question!")
            self.listen(10, self._checkAnswer)

            # Listen for answer, giving hint
            # Give a hint
            
    def stop(self):        
        """ Trivia.stop() | Stops playing trivia. Takes 0 arguments. """
        self.running = False
    
    def _askQuestion(self, question):
        pass
    
    def _checkAnswer(self, question):
        if(question and question["text"] == "test"):
            self.listening = False
            return True
        else:
            return False

    
    
    

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.exit(1)