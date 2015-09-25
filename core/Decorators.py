def command(trigger):
    def decorate(callback):
        def wrapper(self, msg):
            return callback(self, msg)

        if not hasattr(wrapper, 'is_command'):
            wrapper.__name__ = callback.__name__
            setattr(wrapper, 'is_command', True)
            setattr(wrapper, 'is_registered', False)
            setattr(wrapper, 'trigger', trigger)


        return wrapper
    return decorate
