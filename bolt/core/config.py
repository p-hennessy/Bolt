from jsonschema import Draft7Validator, draft7_format_checker
import yaml
import ujson as json
from os.path import join, dirname

DEFAULT_FILE = join(dirname(__file__), "../data/config-defaults.json")
with open(DEFAULT_FILE) as file:
    DEFAULTS = json.load(file)

SCHEMA_FILE = join(dirname(__file__), "../data/config-schema.json")
with open(SCHEMA_FILE) as file:
    SCHEMA = json.load(file)


class Config():
    def __init__(self, config):
        self._raw = config
        for key, value in DEFAULTS.items():
            setattr(self, key, value)

        for key, value in config.items():
            setattr(self, key, value)

    @classmethod
    def from_yaml_file(cls, path):
        with open(path) as config_file:
            config = yaml.safe_load(config_file.read())
            return cls(config)

    @classmethod
    def from_json_file(cls, path):
        with open(path) as config_file:
            config = json.load(config_file)
            return cls(config)

    def validate(self):
        validator = Draft7Validator(
            SCHEMA,
            format_checker=draft7_format_checker
        )
        return [error for error in validator.iter_errors(self._raw)]
