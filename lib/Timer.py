import time

class Timer():
    def __init__(self):
        pass
    
    def start(self):
        self.time = time.time()

    def getElapsedTime(self):
        return time.time() - self.time	