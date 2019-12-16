import unittest
from bolt.core.plugin import Plugin
from bolt import cron
from bolt import Bot

import yaml
from datetime import datetime


class TestCronPlugin(Plugin):
    @cron("* * * * *")
    def crontest(self):
        pass


class TestCron(unittest.TestCase):
    def setUp(self):
        self.config_file = "/tmp/bolt-test-config.yaml"
        fake_config = {
            "api_key": "1234",
            "log_dir": "/tmp/"
        }

        with open(self.config_file, "w") as tempconfig:
            tempconfig.write(yaml.dump(fake_config))

    def test_cron_decos(self):
        bot = Bot(self.config_file)
        plugin = TestCronPlugin(bot)
        plugin.load()

        self.assertTrue(len(plugin.crons) > 0)

    def test_cron_will_run(self):
        bot = Bot(self.config_file)
        plugin = TestCronPlugin(bot)
        plugin.load()

        next_cron = plugin.crons[0].cron.get_current(datetime)
        now = datetime.now()

        self.assertEqual(next_cron.minute, now.minute + 1)
