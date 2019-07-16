import gevent
import time
import logging
from croniter import croniter


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
                        self.logger.debug(
                            f"Scheduling interval callback for: "
                            f"{interval.callback.__self__.__class__.__name__}."
                            f"{interval.callback.__name__}"
                        )
                        interval.last = time.time()
                        self.bot.queue.put((interval.callback, [], {}))

                for cron in plugin.crons:
                    if cron.ready():
                        self.logger.debug(
                            f"Scheduling interval callback for: "
                            f"{interval.callback.__self__.__class__.__name__}."
                            f"{interval.callback.__name__}"
                        )
                        self.bot.queue.put((cron.callback, [], {}))
                        cron.cron.get_next()

            gevent.sleep(1)


class Cron():
    def __init__(self, expression, callback):
        self.expression = expression
        self.callback = callback
        self.cron = croniter(self.expression, time.time())
        self.cron.get_next()

    def ready(self):
        return time.time() >= self.cron.get_current()


class Interval():
    def __init__(self, timeout, callback):
        self.timeout = timeout
        self.callback = callback
        self.last = 0

    def ready(self):
        return int(time.time() - self.last) >= self.timeout
