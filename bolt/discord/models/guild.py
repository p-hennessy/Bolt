from bolt.discord.models.base import Enum, Model, Field, ListField, Snowflake, Timestamp
from bolt.discord.models.channel import Channel
from bolt.discord.models.user import User
from bolt.discord.permissions import Permission


class MessageNotificationLevel(Enum):
    ALL_MESSAGES = 0
    ONLY_MENTIONS = 1


class VerificationLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


class ExplicitContentFilterLevel(Enum):
    DISABLED = 0
    MEMBERS_WITHOUT_ROLES = 1
    ALL_MEMBERS = 2


class MFALevel(Enum):
    NONE = 0
    ELEVATED = 1


class GuildMember(Model):
    __repr_keys__ = ['user']

    user = Field(User)
    guild_id = Field(Snowflake)
    nick = Field(str)
    roles = ListField(int)
    joined_at = Field(Timestamp)
    deaf = Field(bool)
    mute = Field(bool)

    def __repr__(self):
        classname = f"{type(self).__name__}"
        return f"{classname}({repr(self.user)})"

    def kick(self, reason):
        pass

    def ban(self, reason):
        pass

    def set_nickname(self, nickname):
        pass

    def add_role(self):
        pass

    def remove_role(self):
        pass

    @property
    def id(self):
        return self.user.id


class Role(Model):
    __repr_keys__ = ['id', 'name']

    id = Field(Snowflake, required=True)
    name = Field(str, required=True)
    color = Field(int)
    hoist = Field(bool)
    position = Field(int)
    permissions = Field(Permission)
    managed = Field(bool)
    mentionable = Field(bool)


class VoiceState(Model):
    guild_id = Field(Snowflake)
    channel_id = Field(Snowflake)
    user_id = Field(Snowflake)
    session_id = Field(str)
    deaf = Field(bool)
    mute = Field(bool)
    self_deaf = Field(bool)
    self_mute = Field(bool)
    suppress = Field(bool)


class ActivityType(Enum):
    GAME = 0
    STREAMING = 1
    LISTENING = 2


class Activity(Model):
    name = Field(str)
    type = Field(ActivityType)
    url = Field(str)
    application_id = Field(int)
    details = Field(str)
    state = Field(str)
    # timestamps:
    # party:
    # assets:


class Presence(Model):
    __repr_keys__ = ['user']

    user = Field(User)
    game = Field(Activity)
    guild_id = Field(Snowflake)
    status = Field(str)


class Ban(Model):
    reason = Field(str)
    user = Field(User)


class VoiceRegion(Model):
    id = Field(str)
    name = Field(str)
    vip = Field(bool)
    optimal = Field(bool)
    deprecated = Field(bool)
    custom = Field(bool)


class Emoji(Model):
    __repr_keys__ = ['id', 'name']

    id = Field(Snowflake, required=True)
    name = Field(str, required=True)
    roles = ListField(Role)
    user = ListField(User)
    require_colons = Field(bool, default=False)
    managed = Field(bool, default=False)
    animated = Field(bool, default=False)


class Guild(Model):
    __repr_keys__ = ['id', 'name']

    id = Field(Snowflake, required=True)
    name = Field(str)
    icon = Field(str)
    splash = Field(str)
    owner = Field(bool)
    owner_id = Field(Snowflake)
    permissions = Field(Permission)
    region = Field(str)
    afk_channel_id = Field(Snowflake)
    afk_timeout = Field(int)
    embed_enabled = Field(bool)
    embed_channel_id = Field(Snowflake)
    verification_level = Field(VerificationLevel)
    default_message_notifications = Field(MessageNotificationLevel)
    explicit_content_filter = Field(ExplicitContentFilterLevel)
    roles = ListField(Role)
    emojis = ListField(Emoji)
    features = ListField(str)
    mfa_level = Field(MFALevel)
    application_id = Field(Snowflake)
    widget_enabled = Field(bool)
    widget_channel_id = Field(Snowflake)
    system_channel_id = Field(Snowflake)
    joined_at = Field(Timestamp)
    large = Field(bool)
    unavailable = Field(bool)
    member_count = Field(int)
    voice_states = ListField(VoiceState)
    members = ListField(GuildMember)
    channels = ListField(Channel)
    presences = ListField(Presence)
