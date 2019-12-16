from jsonschema import Draft7Validator, draft7_format_checker
import yaml
import ujson as json

from bolt.data import config_defaults, config_schema


class Config():
    def __init__(self, config):
        self._raw = config
        for key, value in config_defaults.items():
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
            config_schema,
            format_checker=draft7_format_checker
        )
        return [error for error in validator.iter_errors(self._raw)]
