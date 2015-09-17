#!/usr/bin/python

from lib.SlackClient import *
from lib.Timer import *

from select import select

import time
import random
import re
import sys

def main():

    connection = SlackConnection("xoxb-6375106610-PiKFtyOj00bOBqTbaqCskYBb")
    connection.connect()

    try:
        while True:
            msg = connection.getMessage()

            if(msg):
                print "MESSAGE: " + str(msg)

    except KeyboardInterrupt:
        connection.killMessageThread()
        connection.disconnect()

class Bot():

    def __init__(self):
        pass

    def login(self):
        

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.exit(1)
