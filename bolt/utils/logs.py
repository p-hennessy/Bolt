"""
    Description:
        FILL ME OUT

    Contributors:
        - Patrick Hennessy
"""
from bolt.core.exceptions import InvalidConfigurationError

from copy import copy
from logging import Formatter
import logging
import os
import sys


def setup_logger(config):
    level, log_dir = get_logging_configuation(config)

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    log = logging.getLogger('')
    log.setLevel(level)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(
        "%(levelname)s %(name)s.%(funcName)s:%(lineno)s '%(message)s'"
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)
    log.addHandler(console_handler)

    # Create log file handler
    file_handler = logging.FileHandler(os.path.join(log_dir, "bot.log"))
    file_formatter = logging.Formatter(
        '{{"time":"{created}","lvl":"{levelname}","src":"{name}.{funcName}:{lineno}","msg":"{message}"}}',
        datefmt='%m/%d/%Y %H:%M:%S',
        style="{"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(level)
    log.addHandler(file_handler)


def get_logging_configuation(config):
    level_name = config.log_level.upper()
    if level_name not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        raise InvalidConfigurationError(f"{level_name} is not a valid log level.")
    level = getattr(logging, level_name)

    log_dir = os.path.abspath(config.log_dir)
    try:
        test_log_file = os.path.join(log_dir, "temp")
        with open(test_log_file, 'a') as _: # noqa: F841
            pass
        os.remove(test_log_file)
    except OSError:
        raise InvalidConfigurationError(f"Log directory at {log_dir} does not exist!")

    return (level, log_dir)


class ColoredFormatter(Formatter):
    def __init__(self, patern):
        Formatter.__init__(self, patern)

    def format(self, record):
        MAPPING = {
            'DEBUG': 36,
            'INFO': 32,
            'WARNING': 33,
            'ERROR': 31,
            'CRITICAL': 41,
        }

        PREFIX = '\033[1;'
        SUFFIX = '\033[0m'

        colored_record = copy(record)
        levelname = colored_record.levelname
        seq = MAPPING.get(levelname, 37)

        colored_levelname = (f'{PREFIX}{seq}m{levelname}{SUFFIX}')
        colored_record.levelname = colored_levelname

        return Formatter.format(self, colored_record)
