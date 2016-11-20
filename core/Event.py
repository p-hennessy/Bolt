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

import logging
logger = logging.getLogger(__name__)

class EventManager():
    def __init__(self, core):
        self.core = core
        self.events = {}


    def register(self, event):
        """Adds an event to so that the bot knows about it

            Args:
                event (str): Name of the event to register

            Returns:
                None
        """
        if event not in self.events:
            self.events[event] = []
        else:
            logger.warning("Event \"{}\" has already been registered".format(event))


    def unregister(self, event):
        """Removes an event so that it can no longer be emmited

            Args:
                event (str): Name of the event to register

            Returns:
                None
        """
        if event in self.events:
            self.events.pop(event, None)
        else:
            logger.warning("Event \"{}\" does not exist.".format(event))


    def notify(self, event, **kwargs):
        """Queues up each event notification to the threadPool

            Args:
                event (str): Name of the event to register

            Returns:
                None
        """
        for callback in self.events[event]:
            self.core.workers.queue(callback, **kwargs)


    def subscribe(self, event, callback):
        """Adds an callback to be invoked when an event occurs

            Args:
                event (str): Name of the event
                callback (bound method): Reference to the method to be called when event occurs

            Returns:
                None
        """
        if callback not in self.events[event]:
            self.events[event].append(callback)
        else:
            logger.warning("Callback \"{}\" was already subscribed to {}.".format(callback, event))

    def unsubscribe(self, event, callback):
        """Removes a callback from an event

            Args:
                event (str): Name of the event
                callback (bound method): Reference to the method to be called when event occurs

            Returns:
                None
        """
        if callback in self.events[event]:
            self.events[event].remove(callback)
        else:
            logger.warning("Callback \"{}\" was not subscribed to any event.".format(callback))
