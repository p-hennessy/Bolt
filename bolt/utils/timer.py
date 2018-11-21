import time
from datetime import timedelta


class Timer():
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
