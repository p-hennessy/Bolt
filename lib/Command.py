class Command():
    def __init__(self, invocation, callback, helptext="", trigger=".", access=0):
        self.invocation = invocation
        self.access = access
        self.trigger = trigger
        self.helptext = helptext
        self.callback = callback
