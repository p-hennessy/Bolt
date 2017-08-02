"""
    Module Name : Decorators

    Description:
        Useful decorators

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""


import time

def Singleton(clazz):
    instance = clazz()
    instance.__call__ = lambda: instance
    return instance

class ttl_cache(object):
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


def interval(delay):
    def decorate(callback):
        def wrapper(self, *args, **kwargs):
            return callback(self, *args, **kwargs)

        return wrapper
    return decorate
