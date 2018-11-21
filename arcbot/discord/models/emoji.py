from arcbot.discord.models.base import DiscordObject
from arcbot.discord.models.user import User

from typing import List


class Emoji(DiscordObject):
    id: int
    name: str
    roles: List[str]
    user: User
    require_colons: bool
    managed: bool
    animated: bool
