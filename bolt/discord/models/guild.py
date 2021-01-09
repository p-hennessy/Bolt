from bolt.discord.models.base import Enum, Model, Field, ListField, Snowflake, Timestamp, SearchableList
from bolt.discord.models.channel import Channel, ChannelType
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


class PremiumTier(Enum):
    NONE = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


class GuildMember(Model):
    __repr_keys__ = ['id', 'name']

    user = Field(User)
    guild_id = Field(Snowflake)
    _nick = Field(str, json_key="nick")
    roles = ListField(int)
    joined_at = Field(Timestamp)
    premium_since = Field(Timestamp)
    deaf = Field(bool)
    mute = Field(bool)
    pending = Field(bool)

    @property
    def mention(self):
        return self.user.mention

    def squelch(self):
        return self.api.modify_guild_member(self.guild_id, self.id, mute=True)

    def unsquelch(self):
        return self.api.modify_guild_member(self.guild_id, self.id, mute=False)

    def deafen(self):
        return self.api.modify_guild_member(self.guild_id, self.id, deaf=True)

    def undeafen(self):
        return self.api.modify_guild_member(self.guild_id, self.id, deaf=False)

    def move(self, channel):
        return self.api.modify_guild_member(self.guild_id, self.id, channel_id=channel.id)

    def whisper(self, *args, **kwargs):
        channel = Channel.marshal(self.api.create_dm(self.id))
        channel.api = self.api
        return channel.say(*args, **kwargs)

    def kick(self):
        return self.api.remove_guild_member(self.guild_id, self.id)

    def ban(self, reason):
        return self.api.create_guild_ban(self.guild_id, self.id, reason=reason)

    def unban(self):
        return self.api.remove_guild_ban(self.guild_id, self.id)

    def nickname(self, nickname):
        raise NotImplementedError

    def add_role(self, role):
        self.api.add_guild_member_role(self.guild_id, self.id, role.id)

    def remove_role(self, role):
        self.api.remove_guild_member_role(self.guild_id, self.id, role.id)

    def has_role(self, role):
        return bool(self.roles.find(id=role.id))

    @property
    def nick(self):
        return self._nick

    @nick.setter
    def nick(self, value):
        self._nick = str(value)

    @property
    def id(self):
        return self.user.id

    @property
    def name(self):
        if self.nick is not None:
            return self.nick
        else:
            return self.user.name


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

    # TODO: Implement update ability

    def rename(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError


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

    def __eq__(self, other):
        return self.user_id == other.user_id


class VoiceRegion(Model):
    id = Field(str)
    name = Field(str)
    vip = Field(bool)
    optimal = Field(bool)
    deprecated = Field(bool)
    custom = Field(bool)


class ActivityType(Enum):
    GAME = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    CUSTOM_STATUS = 4


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


class Emoji(Model):
    __repr_keys__ = ['id', 'name']

    id = Field(Snowflake, required=True)
    name = Field(str, required=True)
    roles = ListField(Role)
    user = ListField(User)
    require_colons = Field(bool, default=False)
    managed = Field(bool, default=False)
    animated = Field(bool, default=False)

    # TODO: Implement Update ability
    def rename(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError


class Guild(Model):
    __repr_keys__ = ['id', 'name']

    id = Field(Snowflake, required=True)
    name = Field(str)
    icon = Field(str)
    icon_hash = Field(str)
    splash = Field(str)
    discovery_splash = Field(str)
    owner = Field(bool)
    owner_id = Field(Snowflake)
    permissions = Field(Permission)
    region = Field(str)
    afk_channel_id = Field(Snowflake)
    afk_timeout = Field(int)
    widget_enabled = Field(bool)
    widget_channel_id = Field(Snowflake)
    verification_level = Field(VerificationLevel)
    default_message_notifications = Field(MessageNotificationLevel)
    explicit_content_filter = Field(ExplicitContentFilterLevel)
    roles = ListField(Role)
    emojis = ListField(Emoji)
    features = ListField(str)
    mfa_level = Field(MFALevel)
    application_id = Field(Snowflake)
    system_channel_id = Field(Snowflake)
    system_channel_flags = Field(int)   # TODO make bit array thing
    rules_channel_id = Field(Snowflake)
    joined_at = Field(Timestamp)
    large = Field(bool)
    unavailable = Field(bool)
    member_count = Field(int)
    voice_states = ListField(VoiceState)
    members = ListField(GuildMember)
    channels = ListField(Channel)
    presences = ListField(Presence)
    max_presences = Field(int)
    max_members = Field(int)
    vanity_url_code = Field(str)
    banner = Field(str)
    premium_tier = Field(PremiumTier)
    premium_subscription_count = Field(int)
    preferred_locale = Field(str)
    public_updates_channel_id = Field(Snowflake)
    max_video_channel_users = Field(int)
    approximate_member_count = Field(int)
    approximate_presence_count = Field(int)

    def leave(self):
        return self.api.leave_guild(self.id)

    def prune(self, days, compute_prune_count=False):
        return self.api.begin_guild_prune(days, compute_prune_count=compute_prune_count)

    def create_voice_channel(self, name, **kwargs):
        response = self.api.create_guild_channel(self.id, name, ChannelType.GUILD_VOICE.value, **kwargs)
        return Channel.marshal(response)

    def create_text_channel(self, name, **kwargs):
        response = self.api.create_guild_channel(self.id, name, ChannelType.GUILD_TEXT.value, **kwargs)
        return Channel.marshal(response)

    def create_category(self, name, **kwargs):
        response = self.api.create_guild_channel(self.id, name, ChannelType.GUILD_CATEGORY.value, **kwargs)
        return Channel.marshal(response)

    @property
    def invites(self):
        return self.api.get_guild_invites(self.id)

    @property
    def prune_count(self):
        return self.api.get_guild_prune_count(self.id)

    @property
    def bans(self):
        all = SearchableList()
        guild_bans = self.api.get_guild_bans(self.id)
        for ban in guild_bans:
            all.append(Ban.marshal(ban))
        return all

    @property
    def embed_channel(self):
        return self.cache.channels[self.embed_channel_id]

    @property
    def widget_channel(self):
        return self.cache.channels[self.widget_channel_id]

    @property
    def afk_channel(self):
        return self.cache.channels[self.afk_channel_id]

    @property
    def system_channel(self):
        return self.cache.channels[self.system_channel_id]

    @property
    def owner(self):
        return self.cache.users[self.owner_id]


class GuildPreview(Model):
    __repr_keys__ = ['id', 'name']

    id = Field(Snowflake, required=True)
    name = Field(str)
    description = Field(str)
    icon = Field(str)
    splash = Field(str)
    discovery_splash = Field(str)
    emojis = ListField(Emoji)
    features = ListField(str)
    approximate_member_count = Field(int)
    approximate_presence_count = Field(int)
