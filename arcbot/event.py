"""
    Class Name : Event

    Description:
        Class to handle event observers

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""
from enum import Enum, auto

import logging
logger = logging.getLogger(__name__)

def subscribe(event):
    def decorate(callback):
        def wrapper(self, *args, **kwargs):
            return callback(self, *args, **kwargs)

        if not hasattr(wrapper, 'is_command'):
            wrapper.__name__ = callback.__name__
            setattr(wrapper, 'is_subscriber', True)
            setattr(wrapper, 'event', event)

        return wrapper
    return decorate

class Events(Enum):
    READY = auto()
    RESUMED = auto()
    CHANNEL_CREATE = auto()
    CHANNEL_UPDATE = auto()
    CHANNEL_DELETE = auto()
    CHANNEL_PINS_UPATE = auto()
    GUILD_CREATE = auto()
    GUILD_UPDATE = auto()
    GUILD_DELETE = auto()
    GUILD_BAN_ADD = auto()
    GUILD_BAN_REMOVE = auto()
    GUILD_EMOJIS_UPDATE = auto()
    GUILD_INTEGRATIONS_UPDATE = auto()
    GUILD_MEMBER_ADD = auto()
    GUILD_MEMBER_REMOVE = auto()
    GUILD_MEMBER_UPDATE = auto()
    GUILD_MEMBERS_CHUNK = auto()
    GUILD_ROLE_CREATE = auto()
    GUILD_ROLE_UPDATE = auto()
    GUILD_ROLE_DELETE = auto()
    MESSAGE_CREATE = auto()
    MESSAGE_UPDATE = auto()
    MESSAGE_DELETE = auto()
    MESSAGE_DELETE_BULK = auto()
    MESSAGE_REACTION_ADD = auto()
    MESSAGE_REACTION_REMOVE = auto()
    MESSAGE_REACTION_REMOVE_ALL = auto()
    PRESENCE_UPDATE = auto()
    TYPING_START = auto()
    USER_UPDATE = auto()
    VOICE_STATE_UPDATE = auto()
    VOICE_SERVER_UPDATE = auto()
    WEBHOOKS_UPDATE = auto()

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
                    for index, value in enumerate(item):
                        yield convert(value)
                return list(yield_convert(item))
            else:
                return item

        return convert(item)

class EventManager():
    def __init__(self):
        self.subscriptions = {}

    def unsubscribe(self, event_id, callback):
        if event_id in self.subscriptions.keys():
            self.subscriptions[event_id].remove(callback)

    def subscribe(self, event_id, callback):
        if event_id not in self.subscriptions.keys():
            self.subscriptions[event_id] = [callback]
        else:
            self.subscriptions[event_id].append(callback)
