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


def command(pattern, access=0, trigger="", silent=False):
    def decorate(callback):
        def wrapper(self, msg):
            return callback(self, msg)

        if not hasattr(wrapper, 'is_command'):
            wrapper.__name__ = callback.__name__
            wrapper.__doc__ = callback.__doc__
            setattr(wrapper, 'is_command', True)
            setattr(wrapper, 'pattern', pattern)
            setattr(wrapper, 'callback', callback)
            setattr(wrapper, 'trigger', trigger)
            setattr(wrapper, 'access', access)
            setattr(wrapper, 'silent', silent)

        return wrapper
    return decorate

def connector(requirement):
    def decorate(callback):
        def wrapper(self, *args, **kwargs):
            return callback(self, *args, **kwargs)

        wrapper.__name__ = callback.__name__
        setattr(wrapper, 'connector', requirement)

        return wrapper
    return decorate

def subscribe(event):
    def decorate(callback):
        def wrapper(self, *args, **kwargs):
            return callback(self, *args, **kwargs)

        if not hasattr(wrapper, 'is_command'):
            wrapper.__name__ = callback.__name__
            setattr(wrapper, 'is_subscriber', True)
            setattr(wrapper, 'event', event)

        return wrapper
    return decorate
