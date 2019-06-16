from bolt.discord.models.base import SearchableList


class Cache():
    def __init__(self):
        self.guilds = SearchableList()
        self.private_channels = SearchableList()
        self.channels = SearchableList()
        self.users = SearchableList()
        self.voice_states = SearchableList()
        self.user = None
