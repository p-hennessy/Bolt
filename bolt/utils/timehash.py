import time
from datetime import datetime


class Timehash():
    def __init__(self, timestamp):
        self.timestamp = int(timestamp)
        
    @classmethod
    def now(cls):
        return cls(time.time())
    
    @classmethod
    def from_hash(cls, hash):
        timestamp = cls.decode(hash)
        return cls(timestamp)
    
    @property
    def datetime(self):
        return datetime.fromtimestamp(self.timestamp)
    
    @property
    def hash(self):
        return self.encode(self.timestamp)
    
    @staticmethod
    def encode(timestamp):
        chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        output = ""
        while timestamp > 0:
            output = chars[int(timestamp % len(chars))] + output
            timestamp = int(timestamp / len(chars))
        return output
    
    @staticmethod
    def decode(hash):
        chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        timehash = hash[::-1]
        epoch = 0
        for i, c in enumerate(timehash):
            epoch += chars.find(c) * (len(chars)**i)
        return epoch
    
    def __repr__(self):
        return f"Timehash({self.timestamp})"
    
    def __str__(self):
        return str(self.hash)

    def __eq__(self, other):
        if isinstance(other, Timehash):
            return self.timestamp == other.timestamp
        else:
            raise TypeError(f"Cannot compare Timehash to {other.__class__.__name__} objects.")
