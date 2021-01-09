from bolt.discord.models.base import Model, Field, Snowflake, Timestamp
from bolt.discord.models.user import User
from bolt.discord.models.guild import Guild


class Template(Model):
    __repr_keys__ = ['code', 'name']

    code = Field(str, required=True)
    name = Field(str)
    description = Field(str)
    usage_count = Field(int)
    creator_id = Field(Snowflake)
    creator = Field(User)
    created_at = Field(Timestamp)
    updated_at = Field(Timestamp)
    source_guild_id = Field(Snowflake)
    serialized_source_guild = Field(Guild)
    is_dirty = Field(bool, default=False)
