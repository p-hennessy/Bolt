import time

class colors():
	reset  = '\033[0m'
	gray = '\033[1;30m' 
	red  = '\033[1;31m'  	
	green  = '\033[1;32m'  	
	yellow  = '\033[1;33m' 	
	white = '\033[1;37m'  
		
class Logger():
    def __init__(self):
        pass
    
    def error(self, message):
        self._consoleOutput(message, colors.red)
    
    def debug(self, message):
        pass
    
    def message(self, message):
        self._consoleOutput(message, colors.reset)
    
    def _consoleOutput(self, message, color, tabLevel=0):
        timestamp = time.strftime("%H:%M:%S")
        date = str(time.strftime("%x")).replace("/", "-")

        print colors.white + "[" + colors.yellow + "Regis Philbot v2.0" + colors.white + "] " + colors.gray + timestamp + " " + color + ("\t" * tabLevel) + message + colors.reset