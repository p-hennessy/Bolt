import gevent
import time

class Scheduler():
    def __init__(self):
        self.items = []
        self.running = False

    def start(self):
        self.running = True

        while self.running:
            if not self.items:
                gevent.sleep(0)
        #
        #
        # while True:
        #     now = time.time()
        #     for item in self.items:
        #         if now - item['last'] >= item['timeout']:
        #             gevent.spawn(callback)
        #
        #     gevent.sleep(1)

    def add(self, timeout, callback):
        pass