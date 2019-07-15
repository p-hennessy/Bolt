from bolt.discord.models.base import SearchableList, SearchableDict
from bolt.discord.events import Subscription
from bolt.utils import snakecase_to_camelcase

class Cache():
    def __init__(self, api):
        self.api = api

        self.guilds = SearchableDict()
        self.private_channels = SearchableDict()
        self.channels = SearchableDict()
        self.users = SearchableDict()
        self.voice_states = SearchableList()
        self.user = None
    
        self.subscriptions = []
        for name, item in self.__class__.__dict__.items():
            if type(item).__name__ == "function" and name.startswith("on_"):
                event_name = snakecase_to_camelcase(name.replace("on_", ""))
                self.subscriptions.append(Subscription(event_name, getattr(self, name)))
            
    def on_ready(self, event):
        for guild in event.guilds:
            guild.api = self.api
            guild.cache = self
            self.guilds[guild.id] = guild
        
        for private_channel in event.private_channels:
            private_channel.api = api
            private_channel.cache = self
            self.private_channels[private_channel.id] = private_channel
    
        self.user = event.user
        self.user.api = self.api
        self.user.cache = self

    def on_channel_create(self, event):
        event.channel.api = self.api
        event.channel.cache = self
        
        self.channels[event.channel.id] = event.channel
        if event.channel.is_guild:
            guild = self.guilds.find(id=event.channel.guild_id)
            guild.channels.append(event.channel)
        elif event.channel.is_dm:
            self.private_channels[event.channel.id] = event.channel
            
    def on_channel_update(self, event):
        self.channels[event.channel.id].merge(event.channel)
        if event.channel.is_guild:
            guild = self.guilds.find(id=event.channel.guild_id)
            channel = guild.channels.find(id=event.channel.id)
            channel.merge(event.channel)

        elif event.channel.is_dm:
            self.private_channels[event.channel.id].merge(event.channel)

    def on_channel_delete(self, event):
        del self.channels[event.channel.id]
        if event.channel.is_guild:
            guild = self.guilds.find(id=event.channel.guild_id)
            channel = guild.channels.find(id=event.channel.id)
            guild.channels.remove(channel)

        elif event.channel.is_dm:
            del self.private_channels[event.channel.id]
        
    def on_channel_pins_update(self, event):
        self.channels[event.channel.id].last_pin_timestamp = event.last_pin_timestamp
        
    def on_guild_create(self, event):
        event.guild.api = self.api
        event.guild.cache = self
        self.guilds[event.guild.id] = event.guild

        for channel in event.guild.channels:
            channel.api = self.api
            channel.cache = self
            channel.guild_id = event.guild.id
            self.channels[channel.id] = channel

        for member in event.guild.members:
            member.api = self.api
            member.user.api = self.api
            member.guild_id = event.guild.id
            self.users[member.id] = member.user
        
        for voice_state in event.guild.voice_states:
            self.voice_states.upsert(voice_state)
    
    def on_guild_update(self, event):
        self.guilds[event.guild.id].merge(event.guild, preserve=[
            'channels', 'members', 'voice_states', 'presences'
        ])
        
    def on_guild_delete(self, event):
        del self.guilds[event.guild.id]
        
    def on_guild_emojis_update(self, event):
        self.guilds[event.guild_id].emojis = event.emojis

    def on_guild_member_add(self, event):
        event.member.api = self.api
        event.member.cache = self
        if event.member.id not in self.users:
            event.member.user.api = self.api
            self.users[event.member.id] = event.member.user
        
        self.guilds[event.member.guild_id].members.append(event.member)
        
    def on_guild_member_remove(self, event):
        member = self.guilds[event.guild_id].members.find(id=event.user.id)
        self.guilds[event.guild_id].members.remove(member)

    def on_guild_member_update(self, event):
        member = self.guilds[event.guild_id].members.find(id=event.user.id)
        member.merge(event.member)

    def on_guild_members_chunk(self, event):
        pass
            
    def on_guild_role_create(self, event):
        event.role.api = self.api
        event.role.cache = self
        self.guilds[event.guild_id].roles.append(event.role)

    def on_guild_role_update(self, event):
        role = self.guilds[event.guild_id].roles.find(id=event.role.id)
        role.merge(event.role)
    
    def on_guild_role_delete(self, event):
        role = self.guilds[event.guild_id].roles.find(id=event.role.id)
        self.guilds[event.guild_id].roles.remove(role)

    def on_message_create(self, event):
        event.message.api = self.api
        event.message.cache = self
        event.message.author.api = self.api
        
        if event.message.channel_id in self.channels:
            self.channels[event.message.channel_id].last_message_id = event.message.id
    
    def on_presence_update(self, event):
        pass
            
    def on_user_update(self, event):
        self.user = event.user
        
    def on_voice_state_update(self, event):
        if event.connected is True:
            existing = event.guild.voice_states.find(user_id=event.voice_state.user_id)
            if existing is None:
                event.guild.voice_states.append(event.voice_state)
        else:
            existing = event.guild.voice_states.find(user_id=event.voice_state.user_id)
            event.guild.voice_states.remove(existing)
            
    def on_webhooks_update(self, event):
        pass
