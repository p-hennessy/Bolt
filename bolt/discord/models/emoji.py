from bolt.discord.models.base import Model, Field, Snowflake, ListField
from bolt.discord.models.user import User
from bolt.discord.models.guild import Role


class Emoji(Model):
    __repr_keys__ = ['id', 'name']

    id = Field(Snowflake)
    name = Field(str, required=True)
    roles = ListField(Role)
    user = ListField(User)
    require_colons = Field(bool, default=False)
    managed = Field(bool, default=False)
    animated = Field(bool, default=False)
