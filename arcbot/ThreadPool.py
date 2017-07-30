"""
    Class Name : Workers

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
import time
import logging
import traceback

from typing import Callable

try:
    import queue
except ImportError:
    import Queue as queue

class ThreadPool():
    def __init__(self, queue_size: int, threads: int):
        self.logger = logging.getLogger(__name__)

        # Init worker list and queue
        self.thread_pool = []
        self.tasks = queue.Queue(queue_size)

        self.logger.info(f"Spawning {threads} worker threads.")

        # Create worker threads
        self.threads = threads

    def queue(self, callable: Callable, *args: list, **kwargs: dict) -> None:
        """
            Puts task on the task queue for workers to pull from.
            If task queue is full; will block until space opens up
        """
        if(self.tasks.full()):
            self.logger.warning("Task queue is full. Consider raising the task queue size.")

        task = (callable, args, kwargs)
        self.tasks.put(task, block=True)

    def dequeue(self) -> None:
        """
            Removes a task from the queue.
            Will block for half a second,
            raises Queue.Empty exception when nothing is in queue
        """
        return self.tasks.get(block=True, timeout=0.1)

    @property
    def threads(self) -> int:
        return len(self.thread_pool)

    @threads.setter
    def threads(self, number: int) -> None:
        while len(self.thread_pool) < number:
            new_worker = Worker(self, len(self.thread_pool) + 1)
            self.thread_pool.append(new_worker)
            new_worker.start()

        while len(self.thread_pool) > number:
            worker = self.thread_pool.pop()
            worker.stop()
            worker.join()

class Worker(threading.Thread):
    def __init__(self, tasks, num):
        # Call super constructor for thread to name it
        super(Worker, self).__init__(name="WorkerThread" + str(num))
        self.name = "WorkerThread" + str(num)
        self.logger = logging.getLogger(self.name)

        # Sentinal value used to kill our thread
        self.running = True

        # Reference to parent object to get tasks from
        self.tasks = tasks

    def stop(self) -> None:
        """
            Tells the thread that it should stop running
        """
        self.running = False

    def run(self) -> None:
        """
            Part of the Thread superclass; this method is where the logic for our thread resides.
            Loops continously while trying to pull a task from the task queue and execute that task
        """
        while(self.running):
            # Dequeue task will block and thread will wait for a task
            try:
                task = self.tasks.dequeue()
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
                self.logger.warning(f"Exception occured in {self.name}:\n {traceback.format_exc()}")
                continue
