from bolt.core.exceptions import InvalidConfigurationError

import yaml


REQUIRED_KEYS = [
    'api_key',
]

DEFAULTS = {
    'log_level': 'DEBUG',
    'mongo_database_username': '',
    'mongo_database_password': '',
    'mongo_database_uri': 'mongodb://localhost:27017',
    'name': 'Bolt',
    'trigger': '.',
    'webhook_port': "1234"
}


class Config():
    def __init__(self, config_path):
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file.read())

        for key, value in DEFAULTS.items():
            setattr(self, key, value)

        for key, value in config.items():
            setattr(self, key, value)

    @staticmethod
    def validate(config_path):
        with open(config_path) as config_file:
            config = yaml.load(config_file.read())

        for key in REQUIRED_KEYS:
            if key not in config:
                raise InvalidConfigurationError(f"Missing required key \"{key}\" in \"{config_path}\"")
