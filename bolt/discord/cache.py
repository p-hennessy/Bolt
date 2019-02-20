class Cache():
    def __init__(self):
        self.guilds = {}
        self.private_channels = {}
        self.channels = {}
        self.users = {}
        self.voice_states = {}
        self.user = None
