"""
    Class Name : ThreadPool

    Description:
        Class that will spawn threads to do work seperate to the main logic
        Objects need call this the *addTask* method to request a worker to do something

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import threading
import time
import logging

try:
    import queue
except ImportError:
    import Queue as queue


class ThreadPool():
    def __init__(self, taskQueueSize, numThreads):
        self.logger = logging.getLogger(__name__)

        # Init worker list and queue
        self.workers = []
        self.tasks = queue.Queue(taskQueueSize)

        self.logger.info("Spawning " + str(numThreads) + " worker threads.")

        # Create worker threads
        for i in range(0, numThreads):
            self.addWorker()

    def queueTask(self, callable, *args, **kwargs):
        """
            Summary:
                Puts task on the task queue for workers to pull from.
                If task queue is full; will block until space opens up

            Args:
                callable (func): Function object to be invoked by a Worker
                *args (list): Positional arguments passed to callable
                **kwargs (dict): Keyword arguments passed to callable

            Returns:
                None
        """
        if(self.tasks.full()):
            self.logger.warning("Task queue is full. Consider raising the task queue size.")

        task = (callable, args, kwargs)
        self.tasks.put(task, block=True)

    def dequeueTask(self):
        """
            Summary:
                Removes a task from the queue. Will block for half a second, and raise Queue.Empty exception when nothing is in queue

            Args:
                None

            Returns:
                None
        """
        return self.tasks.get(block=True, timeout=0.5)

    def addWorker(self):
        """
            Summary:
                Creates and starts a new worker thread

            Args:
                None

            Returns:
                None
        """
        newWorker = Worker(self, len(self.workers) + 1)
        self.workers.append(newWorker)
        newWorker.start()

    def joinThreads(self):
        """
            Summary:
                Will ask threads to halt their execution, and syncronize back with the main thread

            Args:
                None

            Returns:
                None
        """
        for thread in self.workers:
            thread.signalStop()
            thread.join()

class Worker(threading.Thread):
    def __init__(self, pool, num):

        # Call super constructor for thread to name it; Also Python 2.7 requires it
        super(Worker, self).__init__(name="WorkerThread" + str(num))
        self.name = "WorkerThread" + str(num)
        self.logger = logging.getLogger(self.name)

        # Sentinal value used to kill our thread
        self.running = True

        # Reference to parent object to get tasks from
        self.pool = pool

    def signalStop(self):
        """
            Summary:
                Tells the thread that it should stop running

            Args:
                None

            Returns:
                None
        """
        self.running = False

    def run(self):
        """
            Summary:
                Part of the Thread superclass; this method is where the logic for our thread resides.
                Loops continously while trying to pull a task from the ThreadPool's task queue and execute that task

            Args:
                None

            Returns:
                None
        """
        while(self.running):
            # Dequeue task will block and thread will wait for a task
            try:
                task = self.pool.dequeueTask()
            except queue.Empty as e:
                continue

            # Get task data
            callable = task[0]
            args = task[1]
            kwargs = task[2]

            # Invoke task
            try:
                callable(*args, **kwargs)
            except BaseException as e:
                self.logger.warning("Exception occured in {} : {}".format(self.name, str(e)))
                continue
