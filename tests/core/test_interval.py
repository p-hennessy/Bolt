import unittest
from bolt.core.plugin import Plugin
from bolt import interval
from bolt import Bot

import yaml


class TestIntervalPlugin(Plugin):
    @interval(60)
    def intervaltest(self):
        pass


class TestInterval(unittest.TestCase):
    def setUp(self):
        self.config_file = "/tmp/bolt-test-config.yaml"
        fake_config = {
            "api_key": "1234"
        }

        with open(self.config_file, "w") as tempconfig:
            tempconfig.write(yaml.dump(fake_config))

    def test_interval_decos(self):
        bot = Bot(self.config_file)
        plugin = TestIntervalPlugin(bot)
        plugin.load()

        self.assertTrue(len(plugin.intervals) > 0)

    def test_interval_will_run(self):
        bot = Bot(self.config_file)
        plugin = TestIntervalPlugin(bot)
        plugin.load()

        self.assertTrue(plugin.intervals[0].ready())
