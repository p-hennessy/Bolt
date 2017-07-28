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

from typing import Callable

import logging
logger = logging.getLogger(__name__)

class EventManager():
    def __init__(self, core):
        self.core = core
        self.events = {}


    def register(self, event: str):
        if event not in self.events:
            self.events[event] = []
        else:
            logger.warning(f"Event {event} has already been registered")


    def unregister(self, event: str):
        if event in self.events:
            self.events.pop(event, None)
        else:
            logger.warning(f"Event {event} does not exist.")


    def notify(self, event: str, **kwargs):
        for callback in self.events[event]:
            self.core.workers.queue(callback, **kwargs)


    def subscribe(self, event: str, callback: Callable):
        if callback not in self.events[event]:
            self.events[event].append(callback)
        else:
            logger.warning(f"Callback {callback} was already subscribed to {event}.")


    def unsubscribe(self, event: str, callback: Callable):
        if callback in self.events[event]:
            self.events[event].remove(callback)
        else:
            logger.warning(f"Callback {callback} was not subscribed to any event.")
