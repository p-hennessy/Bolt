"""
    Class Name : Main

    Description:
        Entry point for loading CL4M-B0T

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Core import Bot
import logging
import time
import sys

logger = logging.getLogger(__name__)

def main():
    try:
        bot = Bot()
        bot.login()
        bot.watchdog.start()

    except KeyboardInterrupt:
        logger.info("Caught SIGINT from keyboard. Exiting")
        bot.cleanup()
        sys.exit(0)

if __name__ == '__main__':
    main()
