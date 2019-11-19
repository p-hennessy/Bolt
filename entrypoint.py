"""
    Description:
        Entry point for loading Bolt

    Contributors:
        - Patrick Hennessy

    License:
        Bolt is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""
from bolt import Bot
from bolt.core.config import Config

import argparse
import sys
import yaml
import socket
import requests
import os

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from pygments.lexers.python import Python3Lexer


def main():
    parser = init_parser()
    args = vars(parser.parse_args())

    config_path = args.get('config')
    plugin_dir = args.get('plugin_dir')

    if args['command'] == "version":
        version()
    elif args['command'] == "shell":
        run_shell()
    elif args['command'] == "verify-config":
        verify_config(config_path)
    elif args['command'] == "verify-plugins":
        verify_plugins()
    else:
        run_bot(config_path, plugin_dir)


def init_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--config", default='/etc/bolt/config.yml')
    parser.add_argument("--plugin-dir", default='plugins/')

    subparser = parser.add_subparsers(dest='command')
    parser_version = subparser.add_parser('version')
    parser_shell = subparser.add_parser('shell')
    parser_verify_config = subparser.add_parser('verify-config')
    parser_verify_plugins = subparser.add_parser('verify-plugins')

    return parser


def verify_config(config_path):
    config_path = os.path.abspath(config_path)
    errors = Config.validate(config_path)

    RED = "\033[1;31m"
    GREEN = "\033[1;32m"
    RESET = "\033[0m"

    if len(errors) == 0:
        print(f"{GREEN}✔{RESET} Configuration is good!")
        sys.exit(0)
    
    print(f"Invalid configuration at '{config_path}':")
    for error in errors:
        if len(error.path) > 0:
            print(f"{RED}✘{RESET} '{error.path[0]}': {error.message}")
        else:
            print(f"{RED}✘{RESET} {error.message}")
    sys.exit(1)


def verify_plugins():
    pass


def version():
    print(f"{Bot.VERSION}")


def run_bot(config_path, plugin_dir):
    bot = Bot(config_path)
    bot.load_plugin("./plugins/RBAC.py")
    bot.load_plugin("./plugins/Manage.py")
    bot.load_plugin("./plugins/ServeMe.py")
    bot.load_plugin("./plugins/LogsTF.py")
    bot.load_plugin("./plugins/DemosTF.py")
    # bot.load_plugin("./plugins/Pugs.py")
    bot.load_plugin("./plugins/RSS.py")
    bot.load_plugin("./plugins/Chance.py")
    bot.load_plugin("./plugins/Status.py")
    bot.load_plugin("./plugins/Steam.py")
    bot.load_plugin("./plugins/Inspire.py")
    bot.load_plugin("./plugins/UrbanDictionary.py")

    try:
        bot.run()
    except KeyboardInterrupt:
        sys.exit(0)

def run_shell():
    while True:
        with Shell(('127.0.0.1', 5000)) as shell:
            while True:
                try:
                    message = shell.prompt()
                    shell.send(message)
                    print(shell.recv())
                    print()
                except KeyboardInterrupt:
                    continue
                except EOFError:
                    return
                except BrokenPipeError:
                    break


if __name__ == '__main__':
    main()
