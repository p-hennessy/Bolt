from bolt.discord.models.base import Enum, Model, Snowflake, Field, ListField, Timestamp
from bolt.discord.models.emoji import Emoji
from bolt.discord.models.user import User
from bolt.discord.models.guild import Role, GuildMember
from bolt.discord.models.embed import Embed


class MessageType(Enum):
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7


class Reaction(Model):
    count = Field(int, default=1)
    me = Field(bool, default=False)
    emoji = Field(Emoji, required=True)


class Attachment(Model):
    __repr_keys__ = ['id', 'filename']

    id = Field(Snowflake, required=True)
    filename = Field(str, required=True)
    size = Field(int, required=True)
    url = Field(str, required=True)
    proxy_url = Field(str, required=True)
    height = Field(str)
    width = Field(str)


class Message(Model):
    __repr_keys__ = ['id', 'timestamp']

    id = Field(Snowflake, required=True)
    channel_id = Field(Snowflake, required=True)
    guild_id = Field(Snowflake)
    author = Field(User)
    member = Field(GuildMember)
    content = Field(str)
    timestamp = Field(Timestamp)
    edited_timestamp = Field(Timestamp)
    tts = Field(bool, default=False)
    mention_everyone = Field(bool, default=False)
    mentions = ListField(User)
    mention_roles = ListField(Role)
    attachments = ListField(Attachment)
    embeds = ListField(Embed)
    reactions = ListField(Reaction)
    nonce = Field(Snowflake)
    pinned = Field(bool)
    type = Field(MessageType)
    webhook_id = Field(Snowflake)

    def add_reaction(self):
        pass

    def edit(self, content, embed=None):
        pass
