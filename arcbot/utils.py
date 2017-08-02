import os
import importlib
import time
from datetime import timedelta

def find_plugins(path):
    for file in os.listdir(path):
        if not file.startswith('__'):
            if file.endswith("Manage.py"):
                fullname = os.path.splitext(os.path.basename(file))[0]

                try:
                    module = importlib.machinery.SourceFileLoader(fullname, os.path.join(path, file)).load_module()
                except ImportError as e:
                    continue

                yield module

class Timer:
    def __init__(self, percision=3):
        self.percision = percision

    def __enter__(self):
        self.start = time.monotonic()
        self._delta = None
        return self

    def __exit__(self, *args):
        self._delta = timedelta(seconds=time.monotonic()-self.start)
        self._delta = round(self._delta.microseconds / 1000, self.percision)

    @property
    def delta(self):
        if not self._delta:
            self._delta = timedelta(seconds=time.monotonic()-self.start)
            self._delta = round(self._delta.microseconds / 1000, self.percision)

        return self._delta
