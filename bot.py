#!/usr/bin/python

# ************************** #
#     Regis Philbot v1.0     #
#      Slack Trivia Bot	     #
#  		                    #
#             by             #
#      Patrick Hennessy      #
#                            #
#      github.com/ph7vc	     #
# ************************** #

import sys
import BaseHTTPServer
import requests
import urlparse
import simplejson as json
import time
import math
import random

expectedRequestKeys = ['user_id','channel_name','timestamp','team_id','channel_id','token','text','service_id','team_domain','user_name']

config = {}
questions = {}
answerFound = False
bot = None
running = True

def main():
	global bot 
	bot = Trivia()
	random.seed()

	sendMessage(config["botname"] + " initalizing...")
	bot.delay(random.randint(5,20))
	
	while running:
		bot.startTimer()		
		bot.askQuestion()
		
		while bot.getElapsedTime() < 40:
			bot.listenForAnswers()
			
			if (answerFound):
				break

 			if(int(bot.getElapsedTime()) == 20):
 				bot.giveHint()
 				bot.delay(1)
 				
		if not(answerFound):
			bot.giveAnswer()

		bot.delay(random.randint(15,30))	
		
class Trivia():
	currentQuestion = 0
	questionSet = "pokemon"
	timer = time.time()	
	
	def __init__(self):
		global httpd
		httpd = BaseHTTPServer.HTTPServer(('', 69), RequestHandler)
		httpd.socket.settimeout(1)

		prettyPrint("Starting Regis Philbot v1.0")	
	
		loadConfig()
		loadQuestions()
		self.getNextQuestion()
	
	def startTimer(self):
			self.timer = time.time()

	def getElapsedTime(self):
			return time.time() - self.timer	

	def delay(self, seconds):
		time.sleep(seconds)	
	
	def askQuestion(self):
		global answerFound
		answerFound = False
		
		question = questions[self.questionSet][self.currentQuestion]["question"]
		answer = questions[self.questionSet][self.currentQuestion]["answer"]

		if not(question == None):
			prettyPrint("Asking question: " + color.reset + question + "[" + answer + "]")
			sendMessage(question)
		
	def listenForAnswers(self):
		return httpd.handle_request()
		
	def checkAnswer(self, msg):
		answer = questions[self.questionSet][self.currentQuestion]["answer"]
		
		if	( msg.lower() == answer.lower() ):
			return True
		else:
			return False

	def getNextQuestion(self):
		random.seed()		
		
		self.currentQuestion = random.randint(0, len(questions[self.questionSet]) - 1) 		

	def givePoints(self, userid, username):
		self.getNextQuestion()
		prettyPrint("Correct answer given by: " + username, 1)	
		sendMessage("Correct! " + username + ", you earned $10!")
		sendMessage("Your riches have amassed to a staggering $30!")
	
	def giveAnswer(self):
		answer = questions[self.questionSet][self.currentQuestion]["answer"]

		if not(answer == None):		
			prettyPrint("Answer was: " + answer, 1)
			sendMessage("Times up! The answer was: " + answer)
	
		self.getNextQuestion()		
	
	def giveHint(self):
		random.seed()
		answer = questions[self.questionSet][self.currentQuestion]["answer"]
		hint = list("_" * len(answer))
		
		nReveal = int(math.ceil(float(len(answer)) * 0.25))

		for i in range(0, nReveal):
			rand = random.randint(0, nReveal)			
			hint[rand] = answer[rand] 

		finalHint = str("".join(hint))
		
		prettyPrint("Giving hint: " + finalHint,1)
		sendMessage("Heres a hint: " + finalHint)				
	
class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def log_message(self, format, *args):
		return

	def do_GET( self ):
		self.send_response(418)
		self.end_headers()
	  
	def do_POST( self ):
		request_len = int(self.headers['Content-Length'])
		request = self.rfile.read(request_len)

		post = urlparse.parse_qs(request)
		
		# Check key params
		if set(expectedRequestKeys).issubset(post.keys()):
			self.send_response(200)
		else:
			self.send_response(200)
			return
		
		# Check security token
		if not( post["token"][0] == config['outgoingToken'] ):
			self.send_response(200)
			return
		elif ( post["user_name"][0] == 'slackbot' ):
			self.send_response(200)
			return

		self.end_headers()

		if( float(post["timestamp"][0]) < float(bot.timer) ):
			return		
		
		global answerFound

		if(answerFound):
			return
		else:
			answerFound = bot.checkAnswer(post["text"][0])	
		
		if(answerFound):
			bot.givePoints(post["user_id"][0], post["user_name"][0])	
		

# Load config from a file storing into global dict
def loadConfig():
	prettyPrint("Loading config...")
	
	file = open("conf/" + "bot.conf", "r+")
	lines = file.read()
	file.close()
		
	for index in lines.split("\n"):
		split = index.partition("=")
		
		if len(split) == 3:		
			config[split[0]] = split[2]

# Load the questions from a file storing into global dict
def loadQuestions():
	prettyPrint("Loading questions from: \"" + config["questions"] + "\"")
	
	file = open("questions/" + config["questions"], "r")
	
	global questions
	questions = json.load(file)
	
	file.close()

# Aux functions for output stuff
class color():
	reset  = '\033[0m'
	gray = '\033[1;30m' 
	red  = '\033[1;31m'  	
	green  = '\033[1;32m'  	
	yellow  = '\033[1;33m' 	
	white = '\033[1;37m'  
		
def prettyPrint(msg, tabLevel=0):
	timestamp = time.strftime("%H:%M:%S")
	date = str(time.strftime("%x")).replace("/", "-")

	print "\t" + color.white + "[" + color.yellow + "Regis Philbot v1.0" + color.white + "] " + color.gray + timestamp + " " + color.reset + ("\t" * tabLevel) + msg

	file = open("logs/" + date + ".log", "a+")
	file.write( "[Regis Philbot v1.0] " + timestamp + " " + ("\t" * tabLevel) + msg + "\n")	
	file.close()

def sendMessage(msg):
	response = requests.post(config["incomingHookURL"], data='{"channel": "#general", "username": "' + config["botname"] + '", "text":"' + msg + '"}')

	if not(str(response) == "<Response [200]>"):
		prettyPrint(color.red + "ERROR: " + color.reset + "Send message failed.")
		
		global running
		running = False	
			
# Startup function	
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sendMessage(config["botname"] + " shutting down...")
		prettyPrint("Shutting down")
		sys.exit(1)














