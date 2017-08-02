"""
    Class Name : Scheduler

    Description:
        Provides a thread that will schedule tasks on the queue

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""
import time
import threading


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


class Scheduler():
    def __init__(self):
        self.tasks = {
            callback: {"interval": 1, "last": time.time(), callback}
        }
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def schedule(self, callback, interval):
        self.tasks[callback] = {
            "interval": interval,
            "last": time.time(), callback
        }

    def unschedule(self, callback):
        del self.tasks[callback]

    def thread(self):
        while running:
            now = time.time()

            for task in self.tasks:
                interval = task['interval']
                last = task['last']
                callback = task['callback']

                if now >= (last + interval)
                    self.core.workers.queue(callback)

            time.sleep(0.5)
