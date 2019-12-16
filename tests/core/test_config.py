import unittest
from bolt.core.config import Config


class TestConfig(unittest.TestCase):

    def test_invalid_config(self):
        input = {
            "something": False
        }

        config = Config(input)
        errors = config.validate()

        self.assertTrue(len(errors) > 0, "Input invalid configuration but got no errors")

    def test_valid_config(self):
        input = {
            "api_key": "123"
        }

        config = Config(input)
        errors = config.validate()

        self.assertTrue(len(errors) == 0, "Input configuration is invalid")

    def test_attribute_access(self):
        input = {
            "api_key": "123",
            "name": "test"
        }

        config = Config(input)
        errors = config.validate()

        self.assertTrue(len(errors) == 0, "Input configuration is invalid")
        self.assertTrue(config.name == "test")
