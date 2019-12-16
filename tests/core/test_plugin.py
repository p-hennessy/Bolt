import unittest
from bolt.core.plugin import Plugin
from bolt import interval, command, cron, webhook
from bolt import Bot

import yaml


class TestPlugin(Plugin):
    def activate(self):
        self.activated = True

    def deactivate(self):
        self.activated = False

    @webhook("/test")
    def webhooktest(self, request):
        pass

    @command("test123")
    def commandtest(self, event):
        pass

    @cron("* * * * *")
    def crontest(self):
        pass

    @interval(60)
    def intervaltest(self):
        pass


class TestPlugins(unittest.TestCase):
    def setUp(self):
        self.config_file = "/tmp/bolt-test-config.yaml"
        fake_config = {
            "api_key": "1234",
            "log_dir": "/tmp/"
        }

        with open(self.config_file, "w") as tempconfig:
            tempconfig.write(yaml.dump(fake_config))

    def test_name(self):
        bot = Bot(self.config_file)
        plugin = TestPlugin(bot)
        plugin.load()
        self.assertEqual(plugin.name, "TestPlugin")
        self.assertEqual(plugin.logger.name, "plugins.TestPlugin")
        self.assertEqual(repr(plugin), "Plugin(TestPlugin)")

    def test_plugin_activate(self):
        bot = Bot(self.config_file)
        plugin = TestPlugin(bot)
        plugin.load()
        self.assertTrue(plugin.activated)

    def test_plugin_deactivate(self):
        bot = Bot(self.config_file)
        plugin = TestPlugin(bot)
        plugin.load()
        plugin.unload()
        self.assertFalse(plugin.activated)

    def test_cron_decos(self):
        bot = Bot(self.config_file)
        plugin = TestPlugin(bot)
        plugin.load()
        self.assertTrue(len(plugin.crons) > 0)

    def test_interval_decos(self):
        bot = Bot(self.config_file)
        plugin = TestPlugin(bot)
        plugin.load()
        self.assertTrue(len(plugin.intervals) > 0)

    def test_command_decos(self):
        bot = Bot(self.config_file)
        plugin = TestPlugin(bot)
        plugin.load()
        self.assertTrue(len(plugin.commands) > 0)

    def test_webhook_decos(self):
        bot = Bot(self.config_file)
        plugin = TestPlugin(bot)
        plugin.load()
        self.assertTrue(len(plugin.webhooks) > 0)
