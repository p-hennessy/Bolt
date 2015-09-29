"""
    Class Name : ThreadPool

    Description:
        Class that will spawn threads to do work seperate to the main logic

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import threading
import Queue
import time
import logging

class ThreadPool():
    def __init__(self, taskQueueSize, numThreads):
        self.logger = logging.getLogger(__name__)

        self.threads = []
        self.tasks = Queue.Queue(taskQueueSize)

        self.taskQueueSize = taskQueueSize

        self.logger.info("Spawning " + str(numThreads) + " worker threads.")
        for i in range(0, numThreads):
            self.addWorker()

    def queueTask(self, callable, *args, **kwargs):
        """
            Summary:
                Puts task on the task queue

            Args:
                callable (func): Function object to be invoked by a Worker
                *args (list): Positional arguments passed to callable
                **kwargs (dict): Keyword arguments passed to callable

            Returns:
                None
        """
        task = (callable, args, kwargs)
        self.tasks.put(task, block=True)

    def dequeueTask(self):
        """
            Summary:
                Removes a task from the queue

            Args:
                callable (func): Function object to be invoked by a Worker
                *args (list): Positional arguments passed to callable
                **kwargs (dict): Keyword arguments passed to callable

            Returns:
                None
        """
        return self.tasks.get(block=True, timeout=0.5)

    def addWorker(self):
        newThread = Worker(self, len(self.threads) + 1)
        self.threads.append(newThread)
        newThread.start()

    def joinThreads(self):
        for thread in self.threads:
            thread.signalStop()
            thread.join()

class Worker(threading.Thread):
    def __init__(self, pool, num):
        super(Worker, self).__init__(name="WorkerThread" + str(num))
        self.name = "WorkerThread" + str(num)
        self.busy = False
        self.running = True

        self.pool = pool

    def signalStop(self):
        self.running = False

    def run(self):
        while(self.running):
            # Dequeue task will block and thread will wait for a task
            try:
                task = self.pool.dequeueTask()
            except Queue.Empty as e:
                continue

            # Get task data
            callable = task[0]
            args = task[1]
            kwargs = task[2]

            # Invoke task
            callable(*args, **kwargs)
