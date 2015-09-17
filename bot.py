from core import Bot
from lib.ConfigParser import *
import time
import sys

def main():

    regis = Bot()
    regis.login()
    regis.loadPlugins()

    while True:
        time.sleep(1)

    regis.logout()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.exit(1)
