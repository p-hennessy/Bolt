import unittest
from bolt.core.command import Command, RegexCommand, ParseCommand
from bolt.discord.events import MessageCreate
from bolt.discord.models.message import Message


class TestCommand(unittest.TestCase):
    def dummycallback(self):
        pass

    def test_command_matches(self):
        command = Command("test command", self.dummycallback)
        self.assertTrue(command.matches("test command"))

    def test_command_not_matches(self):
        command = Command("test command", self.dummycallback)
        self.assertFalse(command.matches("test"))

    def test_command_args_kwargs(self):
        command = Command("test command", self.dummycallback)
        args, kwargs = command.parse("test command")
        self.assertListEqual(args, [])
        self.assertDictEqual(kwargs, {})

    def test_change_trigger(self):
        command = Command("test command", self.dummycallback, trigger="?!")
        self.assertTrue(command.matches("?!test command"))

    def test_invoke(self):
        def dummycallback(event):
            return True

        event = MessageCreate()
        event.message = Message.marshal({"id": "1", "channel_id": "2", "content": "!test"})
        command = Command("test command", dummycallback, trigger="!")
        self.assertTrue(command.invoke(event))


class TestRegexCommand(unittest.TestCase):

    def dummycallback(self):
        pass

    def test_command_matches(self):
        command = RegexCommand("^test command$", self.dummycallback)
        self.assertTrue(command.matches("test command"))

    def test_command_not_matches(self):
        command = RegexCommand("^test command$", self.dummycallback)
        self.assertFalse(command.matches(" test commanding"))
        self.assertFalse(command.matches("test commanding"))

    def test_command_args_kwargs(self):
        command = RegexCommand("^test command ([0-9]+)$", self.dummycallback)
        args, kwargs = command.parse("test command 1234")
        self.assertListEqual(args, ['1234'])
        self.assertDictEqual(kwargs, {})

    def test_change_trigger(self):
        command = RegexCommand("test command", self.dummycallback, trigger="?!")
        self.assertTrue(command.matches("?!test command"))


class TestParseCommand(unittest.TestCase):

    def dummycallback(self):
        pass

    def test_command_matches(self):
        command = ParseCommand("test command", self.dummycallback)
        self.assertTrue(command.matches("test command"))

    def test_command_not_matches(self):
        command = ParseCommand("test command", self.dummycallback)

        self.assertFalse(command.matches(" test commanding"))
        self.assertFalse(command.matches("test commanding"))

    def test_command_kwargs(self):
        command = ParseCommand("test command {fake_id:d}", self.dummycallback)
        args, kwargs = command.parse("test command 1234")
        self.assertListEqual(args, [])
        self.assertDictEqual(kwargs, {"fake_id": 1234})

    def test_command_args(self):
        command = ParseCommand("test command {:d}", self.dummycallback)
        args, kwargs = command.parse("test command 1234")
        self.assertListEqual(args, [1234])
        self.assertDictEqual(kwargs, {})

    def test_command_args_kwargs(self):
        command = ParseCommand("test command {:d} {fake_thing}", self.dummycallback)
        args, kwargs = command.parse("test command 1234 mortimer")
        self.assertListEqual(args, [1234])
        self.assertDictEqual(kwargs, {"fake_thing": "mortimer"})

    def test_change_trigger(self):
        command = ParseCommand("test command", self.dummycallback, trigger="?!")
        self.assertTrue(command.matches("?!test command"))
