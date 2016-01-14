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

class EventManager():
    def __init__(self, core):
        self.core = core
        self.eventSubscriptions = {}

    def getEvents(self):
        """
            Summary:
                Returns the names of events the bot knows about

            Args:
                None

            Returns:
                (List): Names of events bot knows about
        """
        return self.eventSubscriptions.keys()

    def register(self, event):
        """
            Summary:
                Adds an event to so that the bot knows about it

            Args:
                event (str): Name of the event to register

            Returns:
                None
        """
        if(event in self.eventSubscriptions):
            raise EventRegistrationError("Event already registered")
        else:
            self.eventSubscriptions[event] = []

    def unregister(self, event):
        """
            Summary:
                Removes an event so that it can no longer be emmited.
                This method exists for completion sake

            Args:
                event (str): Name of the event to register

            Returns:
                None
        """
        if(event not in self.eventSubscriptions):
            raise EventRegistrationError("Event does not exist")
        else:
            self.eventSubscriptions.pop(event, None)

    def notify(self, event, **kwargs):
        """
            Summary:
                Queues up each event notification to the threadPool

            Args:
                event (str): Name of the event to register

            Returns:
                None
        """
        for callback in self.eventSubscriptions[event]:
            self.core.threadPool.queueTask(callback, **kwargs)

    def subscribe(self, event, callback):
        """
            Summary:
                Adds an callback to be invoked when an event occurs

            Args:
                event (str): Name of the event
                callback (bound method): Reference to the method to be called when event occurs

            Returns:
                None
        """
        if(callback not in self.eventSubscriptions[event]):
            self.eventSubscriptions[event].append(callback)
        else:
            raise EventSubscriptionError("Callback \"" + str(callback.__name__) + "\" was already subscribed to \"" + event + "\"")

    def unsubscribe(self, event, callback):
        """
            Summary:
                Removes a callback from an event

            Args:
                event (str): Name of the event
                callback (bound method): Reference to the method to be called when event occurs

            Returns:
                None
        """
        if(callback in self.eventSubscriptions[event]):
            self.eventSubscriptions[event].remove(callback)
        else:
            raise EventSubscriptionError("Callback \"" + str(callback.__name__) + "\" was not subscribed to \"" + event + "\"")


class EventRegistrationError(Exception):
    def __init__(self, msg):
        super(CoreSubscriptionError, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg

class EventSubscriptionError(Exception):
    def __init__(self, msg):
        super(CoreSubscriptionError, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg
