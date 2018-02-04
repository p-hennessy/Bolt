from datetime import datetime

from arcbot.discord.models.base import DiscordEnum, DiscordObject, SearchableList, Snowflake
from arcbot.discord.models.channel import Channel
from arcbot.discord.models.user import User
from arcbot.discord.models.emoji import Emoji
from arcbot.discord.permission import Permission

from typing import List


class MessageNotificationLevel(DiscordEnum):
    ALL_MESSAGES = 0
    ONLY_MENTIONS = 1


class VerificationLevel(DiscordEnum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


class ExplicitContentFilterLevel(DiscordEnum):
    DISABLED = 0
    MEMBERS_WITHOUT_ROLES = 1
    ALL_MEMBERS = 2


class MFALevel(DiscordEnum):
    NONE = 0
    ELEVATED = 1


class GuildMember(DiscordObject):
    user: User
    nick: str = ""
    roles: List[int] = []
    joined_at: datetime
    deaf: bool = False
    mute: bool = False

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


class Role(DiscordObject):
    id: Snowflake
    name: str
    color: int
    hoist: bool
    position: int
    permissions: Permission
    managed: bool
    mentionable: bool


class VoiceState(DiscordObject):
    guild_id: Snowflake
    channel_id: Snowflake
    user_id: Snowflake
    session_id: str
    deaf: bool
    mute: bool
    self_deaf: bool
    self_mute: bool
    suppress: bool


class ActivityType(DiscordEnum):
    GAME = 0
    STREAMING = 1
    LISTENING = 2


class Activity(DiscordObject):
    name: str
    type: ActivityType
    url: str
    application_id: int
    details: str
    state: str
    # timestamps:
    # party:
    # assets:


class Presence(DiscordObject):
    user: User
    game: Activity
    guild_id: int = 0
    status: str = ""

    def __repr__(self):
        classname = f"{type(self).__name__}"
        return f"{classname}({repr(self.user)})"


class Guild(DiscordObject):
    id: int
    name: str
    icon: str = ""
    splash: str = ""
    owner: bool = False
    owner_id: int = 0
    permissions: Permission
    region: str = ""
    afk_channel_id: int = 0
    afk_timeout: int = 0
    embed_enabled: bool = False
    embed_channel_id: int = 0
    verification_level: VerificationLevel = VerificationLevel.NONE
    default_message_notifications: MessageNotificationLevel
    explicit_content_filter: ExplicitContentFilterLevel = ExplicitContentFilterLevel.DISABLED
    roles: SearchableList[Role] = []
    emojis: SearchableList[Emoji] = []
    features: SearchableList[str] = []
    mfa_level: MFALevel = MFALevel.NONE
    application_id: int = 0
    widget_enabled: bool = False
    widget_channel_id: int = 0
    system_channel_id: int = 0
    joined_at: str = ""
    large: bool = False
    unavailable: bool = False
    member_count: int = 0
    voice_states: SearchableList[VoiceState] = []
    members: SearchableList[GuildMember] = []
    channels: SearchableList[Channel] = []
    presences: SearchableList[Presence] = []
