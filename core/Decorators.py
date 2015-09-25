# Adds attributes to decorated methods that will be picked up when plugin is loaded
def command(trigger):
    def decorate(callback):
        def wrapper(self, msg):
            return callback(self, msg)

        if not hasattr(wrapper, 'is_command'):
            wrapper.__name__ = callback.__name__
            setattr(wrapper, 'is_command', True)
            setattr(wrapper, 'trigger', trigger)

        return wrapper
    return decorate

def subscriber(event):
    def decorate(callback):
        def wrapper(self, *args, **kwargs):
            return callback(self, *args, **kwargs)

        if not hasattr(wrapper, 'is_command'):
            wrapper.__name__ = callback.__name__
            setattr(wrapper, 'is_subscriber', True)
            setattr(wrapper, 'event', event)

        return wrapper
    return decorate

def publisher(event):
    def decorate(callback):
        def wrapper(self, *args, **kwargs):
            return callback(self, *args, **kwargs)

        if not hasattr(wrapper, 'is_command'):
            wrapper.__name__ = callback.__name__
            setattr(wrapper, 'is_publisher', True)
            setattr(wrapper, 'event', event)

        return wrapper
    return decorate
