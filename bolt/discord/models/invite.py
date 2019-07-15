from bolt.discord.models.base import Model, Field, Timestamp
from bolt.discord.models.guild import Guild
from bolt.discord.models.message import Message
from bolt.discord.models.channel import Channel
from bolt.discord.models.user import User


class Invite(Model):
    code = Field(str)
    guild = Field(Guild)
    channel = Field(Channel)
    target_user = Field(User)
    target_user_type = Field(int)
    approximate_presence_count = Field(int)
    approximate_member_count = Field(int)


class InviteMetadata(Model):
    inviter = Field(User)
    uses = Field(int)
    max_uses = Field(int)
    max_age = Field(int)
    temporary = Field(bool)
    created_at = Field(Timestamp)
    revoked = Field(bool)
