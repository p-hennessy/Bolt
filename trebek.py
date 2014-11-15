#!/usr/bin/python

import sys
import BaseHTTPServer
import urlparse

expectedRequestKeys = ['user_id', 
							'channel_name', 
							'timestamp', 
							'team_id', 
							'channel_id', 
							'token', 
							'text', 
							'service_id', 
							'team_domain', 
							'user_name']

config = {}
answer = ""

class color():
	reset  = '\033[0m' 
	red  = '\033[31m'  	
	green  = '\033[32m'  	
	orange  = '\033[33m' 	
	blue  = '\033[34m'  	
	purple  = '\033[35m'  	
	cyan  = '\033[36m'  	
	gray = '\033[37m'  	
	
	
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
			self.send_response(418)
			return
		
		# Check security token
		if not(post["token"][0] == config['token']):
			self.send_response(418)

		self.end_headers()
		
		checkForAnswer(post['user_id'], post['user_name'], post['text'])

def checkForAnswer(uid, uname, msg):
    print "check answerr"	

def listenForAnswers():
	httpd.handle_request()

def loadConfig():
	file = open("trebek.config", "r+")
	lines = file.read()
	file.close()
		
	for index in lines.split("\n"):

		split = index.split("=")
		
		if len(split) == 2:		
			config[split[0]] = split[1]
			
def init():
	global httpd
	httpd = BaseHTTPServer.HTTPServer(('', 69), RequestHandler)
	httpd.socket.settimeout(2)
	loadConfig()

def main():
	init()
		
	while True:
		question = "Which Pokemon do you start with in Pokemon Yellow version?"
		hint = "p _ k a _ h _" 
		listenForAnswers()
	
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.exit(1)















