import unittest
from bolt.core.config import Config


class TestConfig(unittest.TestCase):

    def test_invalid_config(self):
        input_config = {
            "something": False
        }

        config = Config(input_config)
        errors = config.validate()

        self.assertTrue(len(errors) > 0, "Input invalid configuration but got no errors")

    def test_valid_config(self):
        input_config = {
            "api_key": "123"
        }

        config = Config(input_config)
        errors = config.validate()

        self.assertTrue(len(errors) == 0, "Input configuration is invalid")

    def test_attribute_access(self):
        input_config = {
            "api_key": "123",
            "name": "test"
        }

        config = Config(input_config)
        errors = config.validate()

        self.assertTrue(len(errors) == 0, "Input configuration is invalid")
        self.assertTrue(config.name == "test")
