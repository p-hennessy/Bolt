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

import argparse
import sys
import os
import yaml
import socket
import requests
import importlib.util

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

RED = "\033[1;31m"
GREEN = "\033[1;32m"
RESET = "\033[0m"


def main():
    parser = init_parser()
    args = vars(parser.parse_args())

    config_path = args.get('config')
    plugin_dir = args.get('plugin_dir')

    if args['command'] == "version":
        version()
    elif args['command'] == "verify-config":
        verify_config(config_path)
    elif args['command'] == "verify-plugins":
        verify_plugins()
    else:
        run_bot(config_path, plugin_dir)


def init_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--config", default='pkg/etc/bolt/config.yml')
    parser.add_argument("--plugin-dir", default='plugins/')

    subparser = parser.add_subparsers(dest='command')
    parser_version = subparser.add_parser('version')
    parser_verify_config = subparser.add_parser('verify-config')
    parser_verify_plugins = subparser.add_parser('verify-plugins')

    return parser


def verify_config(config_path):
    exit_error = False

    with open(config_path) as config_file:
        config = yaml.load(config_file.read())

    required_keys = [
        'api_key',
    ]

    defaults = {
        'log_format': 'json',
        'log_level': 'DEBUG',
        'mongo_database_username': '',
        'mongo_database_password': '',
        'mongo_database_uri': 'mongodb://localhost:27017',
        'name': 'Bolt',
        'trigger': '.',
        'webhook_port': "1234"
    }

    for key, value in config.items():
        value = str(value)
        if len(value) <= 0:
            if key in required_keys:
                print(f"{RED}✘{RESET} Configuation option \"{key}\" needs a valid value")
                exit_error = True
            else:
                config[key] = defaults[key]


    # Test API key with Discord
    response = requests.get(
        "https://discordapp.com/api/gateway/bot",
        headers={
            "authorization": "Bot " + config['api_key'],
            "Content-Type": 'application/json'
        }
    )
    if not response.ok:
        print(f"{RED}✘{RESET} Invalid Discord token provided")
        exit_error = True
    else:
        print(f"{GREEN}✔{RESET} Able to connect to Discord with provided token")

    # Test connection to Mongo
    try:
        database_client = MongoClient(
            config['mongo_database_uri']
        )
        database_client.admin.command('ismaster')
        database_client.close()
        print(f"{GREEN}✔{RESET} Able to connect to MongoDB server with provided credentials")
    except ConnectionFailure:
        print(f"{RED}✘ {RESET} MongoDB server \"{config['mongo_database_uri']}\" not available")
        exit_error = True

    # Check if webhook port is already in use
    if is_port_in_use(config['webhook_port']):
        print(f"{RED}✘ {RESET} Webhook port \"{config['webhook_port']}\" is already in use")
        exit_error = True
    else:
        print(f"{GREEN}✔{RESET} Webhook port \"{config['webhook_port']}\" is available")

    sys.exit(int(exit_error))


def verify_plugins():
    pass


def version():
    print(f"{Bot.VERSION}")


def run_bot(config_path, plugin_dir):
    bot = Bot(config_path)
    bot.load_plugin("./plugins/Access.py")
    bot.load_plugin("./plugins/Manage.py")
    bot.load_plugin("./plugins/Chance.py")
    bot.load_plugin("./plugins/DemosTF.py")
    bot.load_plugin("./plugins/LogsTF.py")
    bot.load_plugin("./plugins/Steam.py")
    bot.load_plugin("./plugins/UrbanDictionary.py")
    bot.load_plugin("./plugins/ServeMe.py")

    try:
        bot.run()
    except KeyboardInterrupt:
        sys.exit(0)


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


if __name__ == '__main__':
    main()
