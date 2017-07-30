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
