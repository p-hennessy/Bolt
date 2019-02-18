"""
    Description:
        Class to handle event observers

    Contributors:
        - Patrick Hennessy
"""

from bolt.discord.events import Events


class Event():
    def __init__(self):
        pass

    @classmethod
    def from_message(cls, message):
        event = cls.to_object(message["d"])
        event.name = getattr(Events, message["t"])
        event.sequence = message["s"]

        return event

    @classmethod
    def to_object(cls, item):
        def convert(item):
            if isinstance(item, dict):
                return type('Event', (), {k: convert(v) for k, v in item.items()})
            if isinstance(item, list):
                def yield_convert(item):
                    for _, value in enumerate(item):
                        yield convert(value)
                return list(yield_convert(item))
            else:
                return item

        return convert(item)


class Subscription():
    def __init__(self, event, callback):
        self.event = event
        self.callback = callback
