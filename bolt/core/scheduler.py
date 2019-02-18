import gevent
import time
import logging


class Scheduler():
    def __init__(self, bot):
        self.running = False
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    def start(self):
        self.logger.debug('Spawning Scheduler Greenlet')
        self.running = True

        while self.running:
            for plugin in self.bot.plugins:
                if not plugin.enabled:
                    continue

                for interval in plugin.intervals:
                    if interval.ready():
                        interval.last = time.time()
                        self.bot.queue.put((interval.callback, [], {}))

            gevent.sleep(1)


class Interval():
    def __init__(self, timeout, callback):
        self.timeout = timeout
        self.callback = callback
        self.last = 0

    def ready(self):
        return int(time.time() - self.last) >= self.timeout
