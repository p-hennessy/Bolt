from bolt.discord.models.base import Snowflake, Model, Field, Enum


class PremiumType(Enum):
    NITROCLASSIC = 1
    NITRO = 2


class User(Model):
    __repr_keys__ = ['id', 'name']

    id = Field(Snowflake, required=True, immutable=True)
    name = Field(str, json_key="username")
    discriminator = Field(str)
    avatar = Field(str, default=None)
    bot = Field(bool, default=False)
    mfa_enabled = Field(bool, default=False)
    locale = Field(str)
    verified = Field(bool, default=False)
    email = Field(str)
    flags = Field(int)
    premium_type = Field(PremiumType)

    def whisper(self):
        pass
