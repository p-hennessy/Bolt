import logging

class Config():
    def __init__(self):
        self.name = "Arcbot"
        self.trigger = "arcbot "
        self.log_level = logging.INFO

        self.threads = 12
        self.queue_size = 100

        self.connection_retry = 3
        self.connection_timeout = 300
