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
    def __init__(self):
        self.eventSubscriptions = {}

    def getEvents(self):
        return self.eventSubscriptions.keys()

    def register(self, event):
        if(event in self.eventSubscriptions):
            raise EventRegistrationError("Event already registered")
        else:
            self.eventSubscriptions[event] = []

    def unregister(self, event):
        if(event not in self.eventSubscriptions):
            raise EventRegistrationError("Event does not exist")
        else:
            self.eventSubscriptions.pop(event, None)

    def notify(self, event, **kwargs):
        for callback in self.eventSubscriptions[event]:
            callback(**kwargs)

    def subscribe(self, event, callback):
        if(callback not in self.eventSubscriptions[event]):
            self.eventSubscriptions[event].append(callback)
            return True
        else:
            raise EventSubscriptionError("Callback \"" + str(callback.__name__) + "\" was already subscribed to \"" + event + "\"")

    def unsubscribe(self, event, callback):
        if(callback in self.eventSubscriptions[event]):
            self.eventSubscriptions[event].remove(callback)
            return True
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
