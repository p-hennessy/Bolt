from arcbot.discord.models.base import DiscordEnum, DiscordObject, Snowflake
from arcbot.discord.models.emoji import Emoji
from arcbot.discord.models.user import User
from arcbot.discord.models.guild import Role
from arcbot.discord.models.embed import Embed

from datetime import datetime
from typing import List


class MessageType(DiscordEnum):
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7


class Reaction(DiscordObject):
    count: int
    me: bool
    emoji: Emoji


class Attachment(DiscordObject):
    id: Snowflake
    filename: str
    size: int
    url: str
    proxy_url: str
    height: int
    width: int


class Message(DiscordObject):
    id:	Snowflake
    channel_id:	Snowflake
    author: User
    content: str
    timestamp: datetime
    edited_timestamp: datetime
    tts: bool
    mention_everyone: bool
    mentions: List[User]
    mention_roles: List[Role]
    attachments: List[Attachment]
    embeds: List[Embed]
    reactions: List[Reaction]
    nonce: Snowflake
    pinned: bool
    webhook_id: Snowflake
    type: MessageType
    arguments: List[None] = []
