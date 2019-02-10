from bolt.discord.models.base import Snowflake, Model, Field, ListField, Enum, Timestamp
from bolt.discord.models.user import User
from bolt.discord.permissions import Permission

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
