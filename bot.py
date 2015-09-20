"""
    Class Name : Main

    Description:
        Entry point for loading PhilBot

    Contributors:
        - Patrick Hennessy

    License:
        PhilBot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Core import Bot
import time
import sys

def main():

    Philbot = Bot()

    while True:
        time.sleep(1)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.exit(1)
