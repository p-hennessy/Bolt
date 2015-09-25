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
import time
import sys

from colorlog import ColoredFormatter
import logging

def main():
    logging.getLogger("requests").setLevel(logging.WARNING)

    logger = logging.getLogger('')

    console_hdlr = logging.StreamHandler(sys.stdout)
    formatter = ColoredFormatter(
        "%(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)-25.25s%(reset)s %(white)s%(message)s%(reset)s",
        datefmt="[%m/%d/%Y %H:%M:%S]",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bg_red',
        }
    )

    console_hdlr.setFormatter(formatter)
    logger.addHandler(console_hdlr)
    logger.setLevel(logging.INFO)

    bot = Bot()

    while True:
        time.sleep(1)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.exit(1)
