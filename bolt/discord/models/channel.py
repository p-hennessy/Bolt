from bolt.discord.models.base import Snowflake, Model, Field, ListField, Enum, Timestamp, SearchableList
from bolt.discord.models.user import User
from bolt.discord.permissions import Permission

import os

class ChannelType(Enum):
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4


class PermissionOverwrite(Model):
    __repr_keys__ = ['id', 'type']

    id = Field(Snowflake)
    type = Field(str)
    deny = Field(Permission)
    allow = Field(Permission)


class Channel(Model):
    __repr_keys__ = ['id', 'name', 'type']

    id = Field(Snowflake, required=True)
    type = Field(ChannelType, required=True)
    guild_id = Field(Snowflake)
    position = Field(int)
    permission_overwrites = ListField(PermissionOverwrite)
    name = Field(str, max_length=100)
    topic = Field(str, max_length=1024)
    nsfw = Field(bool)
    last_message_id = Field(Snowflake)
    bitrate = Field(int)
    user_limit = Field(int)
    rate_limit_per_user = Field(int)
    recipients = ListField(User)
    icon = Field(str)
    owner_id = Field(Snowflake)
    application_id = Field(Snowflake)
    parent_id = Field(Snowflake)
    last_pin_timestamp = Field(Timestamp)

    def update(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def create_invite(self):
        raise NotImplementedError

    def create_webhook(self):
        raise NotImplementedError
    
    def upload(self, files=[]):
        all_files = {os.path.basename(file):open(file, 'rb') for file in files}
        return self.bot.api.create_message(files=all_files, headers=self.auth_headers)

    def say(self, message="", embed=None, mentions=None):
        embed = {} if embed is None else embed
        mentions = [] if mentions is None else mentions

        for user in mentions:
            message = f"{user.mention} {message}"

        message_data = {"content": message, "embed": embed}
        
        return self.api.create_message(self.id, message_data)
            
    def trigger_typing(self):
        return self.api.trigger_typing(self.id)

    def bulk_delete_messages(self):
        raise NotImplementedError
    
    @property
    def voice_members(self):
        if self.type == ChannelType.GUILD_VOICE:
            return self.guild.voice_states.filter(lambda vs: vs.channel_id == self.id)
    
    @property
    def guild(self):
        return self.cache.guilds[self.guild_id]
    
    @property
    def webhooks(self):
        raise NotImplementedError
    
    @property
    def pins(self):
        # Something about circular imports?
        from bolt.discord.models.message import Message

        all_pins = SearchableList()
        messages = self.api.get_pinned_messages(self.id)
        for message in messages:
            all_pins.append(Message.marshal(message))
        
        return all_pins
    
    @property
    def is_dm(self):
        return self.type in [ChannelType.DM, ChannelType.GROUP_DM]
    
    @property
    def is_guild(self):
        return self.type in [ChannelType.GUILD_TEXT, ChannelType.GUILD_VOICE, ChannelType.GUILD_CATEGORY]
