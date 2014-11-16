#!/usr/bin/python

# ************************** #
#        Trebek v 1.0        #
#      Slack Trivia Bot	     #
#  		                    #
#             by             #
#      Patrick Hennessy      #
#                            #
#      github.com/ph7vc	     #
# ************************** #

import sys
import BaseHTTPServer
import urlparse
import simplejson as json
import time

expectedRequestKeys = ['user_id','channel_name','timestamp','team_id','channel_id','token','text','service_id','team_domain','user_name']

config = {}
questions = {}
answerFound = False
trebek = None

def main():
	global trebek 
	trebek = Trivia()

	while True:
		trebek.startTimer()		
		trebek.askQuestion()
		
		while trebek.getElapsedTime() < 5:
			trebek.listenForAnswers()
			
			if (answerFound):
				print "Answer Found!"
				break

 			if(int(trebek.getElapsedTime()) == 15):
 				print "Hint 1"
 			elif(int(trebek.getElapsedTime()) == 45):
 				print "Hint 2"
 				
		if(answerFound):
			trebek.givePoints()
		else:
			trebek.giveAnswer()

		trebek.delay(5)		
		
class Trivia():
	currentQuestion = 0
	questionSet = "pokemon"
	timer = time.time()	
	
	def __init__(self):
		global httpd
		httpd = BaseHTTPServer.HTTPServer(('', 69), RequestHandler)
		httpd.socket.settimeout(1)

		prettyPrint("Starting Trebek 1.0")	
	
		loadConfig()
		loadQuestions()
	
	def startTimer(self):
			self.timer = time.time()

	def getElapsedTime(self):
			return time.time() - self.timer	

	def delay(self, seconds):
		time.sleep(seconds)	
	
	def askQuestion(self):
		global answerFound
		answerFound = False

		prettyPrint(color.white + "> Asking question: " + color.reset + questions[self.questionSet][self.currentQuestion]["question"])
		
	def listenForAnswers(self):
		return httpd.handle_request()
		
	def checkAnswer(self, answer):
		print "checking for answer"
		return False

	def getNextQuestion(self):
		if(len(questions["pokemon"]) - 1 == self.currentQuestion):
			self.currentQuestion = 0
	
		else:
			self.currentQuestion += 1

	def givePoints(self):
		self.getNextQuestion()
		print "10 pints!"	
	
	def giveAnswer(self):
		self.getNextQuestion()	
		print "Answer was xxx..."
	
	def giveHint(self):
		print "giving hint"
	
	
class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
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
			self.send_response(418) # Tell the client about your teapot-ness
			return
		
		# Check security token
		if not(post["token"][0] == config['token']):
			self.send_response(418)

		self.end_headers()
		
		global answerFound
		answerFound = trebek.checkAnswer(post["text"])		
		

# Load config from a file storing into global dict
def loadConfig():
	prettyPrint("Loading config...")
	
	file = open("trebek.config", "r+")
	lines = file.read()
	file.close()
		
	for index in lines.split("\n"):
		split = index.split("=")
		
		if len(split) == 2:		
			config[split[0]] = split[1]

# Load the questions from a file storing into global dict
def loadQuestions():
	prettyPrint("Loading questions from: \"" + config["questions"] + "\"")
	
	file = open(config["questions"], "r")
	
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
	blue  = '\033[1;34m'  	
	purple  = '\033[1;35m'  	
	cyan  = '\033[1;36m'  	
	white = '\033[1;37m'  
		
def prettyPrint(msg, tabLevel=0):
	print "\t" + color.white + "[" + color.yellow + "Trebek v1.0" + color.white + "] " + color.reset + ("\t" * tabLevel) + msg
	
# Startup function	
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.exit(1)















# ************************** #