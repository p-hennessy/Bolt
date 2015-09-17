class Command():
    def __init__(self, invocation, callback, trigger=".", access=0):
        self.invocation = invocation
        self.access = access
        self.trigger = trigger
        self.callback = callback
