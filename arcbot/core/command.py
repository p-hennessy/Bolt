"""
    Description:
        Classes that manage commands

    Contributors:
        - Patrick Hennessy
"""
import re
import parse
import logging
logger = logging.getLogger(__name__)


class Command():
    def __init__(self, pattern, callback, trigger="", access=0):
        self.pattern = pattern
        self.access = access
        self.callback = callback
        self.trigger = trigger

    def __str__(self):
        return self.callback.__name__

    def __repr__(self):
        classname = f"{type(self).__name__}"
        return f"{classname}({self.callback.__class__.__name__}.{self.callback.__name__})"

    def invoke(self, message):
        message.content = message.content.replace(self.trigger, "", 1)
        self.callback(message)

    def matches(self, text):
        if text.startswith(self.trigger):
            text = text.replace(self.trigger, "", 1)
            return self.pattern == text
        else:
            return False

    def parse(self, text):
        return [], {}


class RegexCommand(Command):
    def __init__(self, pattern, *args, **kwargs):
        self.compiled_pattern = re.compile(pattern)
        super(RegexCommand, self).__init__(pattern, *args, **kwargs)

    def matches(self, text):
        if text.startswith(self.trigger):
            text = text.replace(self.trigger, "", 1)
            match = self.compiled_pattern.search(text)

            return match is not None
        else:
            return False

    def parse(self, text):
        text = text.replace(self.trigger, "", 1)
        result = self.compiled_pattern.search(text)

        args = list(result.groups()) or []
        kwargs = {}

        return args, kwargs


class ParseCommand(Command):
    def __init__(self, pattern, *args, **kwargs):
        self.compiled_pattern = parse.compile(pattern)
        super(ParseCommand, self).__init__(pattern, *args, **kwargs)

    def matches(self, text):
        if text.startswith(self.trigger):
            text = text.replace(self.trigger, "", 1)
            match = self.compiled_pattern.parse(text)

            return match is not None
        else:
            return False

    def parse(self, text):
        text = text.replace(self.trigger, "", 1)
        result = self.compiled_pattern.parse(text)

        args = list(result.fixed) or []
        kwargs = dict(result.named) or {}

        return args, kwargs
