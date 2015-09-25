"""
    Class Name : Main

    Description:
        Entry point for loading CL4M-B0T

    Contributors:
        - Patrick Hennessy

    License:
        CL4M-B0T is free software: you can redistribute it and/or modify it
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

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Caught SIGINT from keyboard. Exiting")
        sys.exit(0)

if __name__ == '__main__':
    main()
