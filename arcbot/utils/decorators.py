import time

def add_method_tag(metadata):
    def decorate(callback):
        if not hasattr(callback, 'metadata'):
            callback.tags = []

        callback.tags.append(metadata)

        return callback
    return decorate

class cache(object):
    def __init__(self, ttl):
        self.cache = {}
        self.ttl = ttl

    def __call__(self, callback):
        def wrapper(*args):
            now = time.time()
            try:
                value, last_update = self.cache[args]
                if self.ttl > 0 and now - last_update > self.ttl:
                    raise AttributeError

                return value
            except (KeyError, AttributeError):
                value = callback(*args)
                self.cache[args] = (value, now)

                return value
            except TypeError:
                return callback(*args)
        return wrapper
