
import time

class Watchdog():
    def __init__(self, core):
        self.core = core

    def start(self):
        while True:
            time.sleep(1000)
