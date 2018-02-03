from arcbot.discord.models.base import *
from arcbot.discord.models.user import User

class Emoji(DiscordObject):
    id: int
    name: str
    roles: List[str]
    user: User
    require_colons: bool
    managed: bool
    animated: bool
