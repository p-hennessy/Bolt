import gevent
import time
import logging

class Scheduler():
    def __init__(self, bot):
        self.tasks = []
        self.running = False
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    def start(self):
        self.logger.debug('Spawning Scheduler Greenlet')
        self.running = True

        while self.running:
            if not self.tasks:
                gevent.sleep(1)

            now = time.time()
            for task in self.tasks:
                if int(now - task['last']) >= task['timeout']:
                    task['last'] = time.time()
                    self.bot.queue.put((task['callback'], [], {}))

            gevent.sleep(1)

    def run_interval(self, callback, timeout):
        new_task = {
            'timeout': timeout,
            'last': 0,
            'callback': callback
        }
        self.tasks.append(new_task)

    def run_cron(self):
        raise NotImplemented

    def run_later(self, timestamp):
        raise NotImplemented
        
        new_task = {
            'timestamp': timestamp,
            'callback': callback
        }
        self.tasks.append(new_task)
