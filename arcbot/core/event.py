"""
    Description:
        Class to handle event observers

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""
import logging


class EventManager():
    def __init__(self):
        self.subscriptions = {}
        self.logger = logging.getLogger(__name__)

    def unsubscribe(self, event_id, callback):
        if event_id in self.subscriptions.keys():
            self.subscriptions[event_id].remove(callback)

    def subscribe(self, event_id, callback):
        if event_id not in self.subscriptions.keys():
            self.subscriptions[event_id] = [callback]
        else:
            self.subscriptions[event_id].append(callback)
