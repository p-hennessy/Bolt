from bolt.discord.models.base import Enum, Model, Snowflake, Field, ListField, Timestamp
from bolt.discord.models.emoji import Emoji
from bolt.discord.models.user import User
from bolt.discord.models.guild import Role, GuildMember
from bolt.discord.models.embed import Embed
from bolt.discord.models.channel import ChannelMention


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


class StickerFormat(Enum):
    PNG = 1
    APNG = 2
    LOTTIE = 3


class Sticker(Model):
    id = Field(Snowflake, required=True)
    pack_id = Field(Snowflake, required=True)
    name = Field(str, required=True)
    description = Field(str, required=True)
    tags = Field(str)
    asset = Field(str)
    preview_asset = Field(str)
    format_type = Field(StickerFormat)


class Attachment(Model):
    __repr_keys__ = ['id', 'filename']

    id = Field(Snowflake, required=True)
    filename = Field(str, required=True)
    size = Field(int, required=True)
    url = Field(str, required=True)
    proxy_url = Field(str, required=True)
    height = Field(str)
    width = Field(str)


class MessageApplication(Model):
    id = Field(Snowflake, required=True)
    cover_image = Field(str)
    description = Field(int, required=True)
    icon = Field(str, required=True)
    name = Field(str, required=True)


class MessageActivityType(Enum):
    JOIN = 0
    SPECTATE = 1
    LISTEN = 2
    JOIN_REQUEST = 3


class MessageActivity(Model):
    type = Field(MessageActivityType)
    party_id = Field(Snowflake)


class MessageReference(Model):
    message_id = Field(Snowflake)
    channel_id = Field(Snowflake)
    guild_id = Field(Snowflake)


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
    mention_channels = ListField(ChannelMention)
    attachments = ListField(Attachment)
    embeds = ListField(Embed)
    reactions = ListField(Reaction)
    nonce = Field(Snowflake)
    pinned = Field(bool)
    webhook_id = Field(Snowflake)
    type = Field(MessageType)
    activity = Field(MessageActivity)
    application = Field(MessageApplication)
    message_reference = Field(MessageReference)
    flags = Field(int)
    strickers = ListField(Sticker)

    def add_reaction(self):
        pass

    def edit(self, message="", embed=None, mentions=None):
        self.content = message
        self.embed = embed

        embed = embed if embed is not None else self.embed
        mentions = mentions if mentions is not None else self.mentions

        for user in mentions:
            message = f"{user.mention} {message}"

        message_data = {"content": message, "embed": embed}
        self.api.edit_message(self.channel_id, self.id, message_data)

    def reply(self, message):
        self.channel.say(message, mentions=[self.author])

    @property
    def member(self):
        # TODO error handling around if guild
        return self.guild.members.find(id=self.author.id)

    @property
    def is_guild(self):
        return self.guild_id is not None

    @property
    def is_dm(self):
        return self.guild_id is None

    @property
    def channel(self):
        return self.cache.channels[self.channel_id]

    @property
    def guild(self):
        return self.cache.guilds[self.guild_id]
