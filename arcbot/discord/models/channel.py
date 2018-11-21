from arcbot.discord.models.base import DiscordEnum, DiscordObject, Snowflake
from arcbot.discord.models.user import User
from arcbot.discord.permission import Permission

from datetime import datetime
from typing import List


class ChannelType(DiscordEnum):
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4


class PermissionOverwrite(DiscordObject):
    type:  str
    id: Snowflake
    deny: Permission
    allow: Permission


class Channel(DiscordObject):
    id: Snowflake
    type: ChannelType
    guild_id: Snowflake
    position: int
    permission_overwrites: List[PermissionOverwrite] = []
    name: str
    topic: str
    nsfw: bool
    last_message_id: Snowflake
    bitrate: int
    user_limit: int
    recipients: List[User] = []
    icon: str
    owner_id: Snowflake
    application_id: Snowflake
    parent_id: Snowflake
    last_pin_timestamp: datetime
