from arcbot.discord.models.base import DiscordObject, Snowflake


class User(DiscordObject):
    id: Snowflake
    username: str
    discriminator: str = "0000"
    avatar: str = ""
    bot: bool = False
    mfa_enabled: bool = False
    verified: bool = False
    email: str = ""
