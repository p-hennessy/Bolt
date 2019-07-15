from bolt.discord.models.user import User
from bolt.discord.models.base import Snowflake, Timestamp, Model, Field, ListField
from bolt.discord.models.message import Reaction, Message
from bolt.discord.models.guild import Guild, GuildMember, VoiceState, Role
from bolt.discord.models.emoji import Emoji
from bolt.discord.models.channel import Channel
from bolt.utils import snakecase_to_camelcase

from enum import Enum, auto
import gevent
import logging

class Subscription():
    def __init__(self, event_name, callback):
        self.event_name = event_name
        self.callback = callback

class Events(Enum):
    READY = auto()
    RESUMED = auto()
    CHANNEL_CREATE = auto()
    CHANNEL_UPDATE = auto()
    CHANNEL_DELETE = auto()
    CHANNEL_PINS_UPDATE = auto()
    GUILD_CREATE = auto()
    GUILD_UPDATE = auto()
    GUILD_DELETE = auto()
    GUILD_BAN_ADD = auto()
    GUILD_BAN_REMOVE = auto()
    GUILD_EMOJIS_UPDATE = auto()
    GUILD_INTEGRATIONS_UPDATE = auto()
    GUILD_MEMBER_ADD = auto()
    GUILD_MEMBER_REMOVE = auto()
    GUILD_MEMBER_UPDATE = auto()
    GUILD_MEMBERS_CHUNK = auto()
    GUILD_ROLE_CREATE = auto()
    GUILD_ROLE_UPDATE = auto()
    GUILD_ROLE_DELETE = auto()
    MESSAGE_CREATE = auto()
    MESSAGE_UPDATE = auto()
    MESSAGE_DELETE = auto()
    MESSAGE_DELETE_BULK = auto()
    MESSAGE_REACTION_ADD = auto()
    MESSAGE_REACTION_REMOVE = auto()
    MESSAGE_REACTION_REMOVE_ALL = auto()
    PRESENCE_UPDATE = auto()
    TYPING_START = auto()
    USER_UPDATE = auto()
    VOICE_STATE_UPDATE = auto()
    VOICE_SERVER_UPDATE = auto()
    WEBHOOKS_UPDATE = auto()

    def __repr__(self):
        return f"{self.__class__.__name__}.{self._name_}"

class EventHandler():
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    def dispatch(self, event, subscriptions, async=False):
        for subscription in subscriptions:
            event_name = snakecase_to_camelcase(event.name)
            if subscription.event_name == event_name:
                self.logger.debug(
                    f"Dispatching \"{event_name}\" to "
                    f"{subscription.callback.__self__.__module__}."
                    f"{subscription.callback.__self__.__class__.__name__}."
                    f"{subscription.callback.__name__}"
                )
            
                if async is True:
                    self.bot.queue.put((subscription.callback, [event], {}))
                    gevent.sleep(0)
                    continue
                else:
                    subscription.callback(event)

class GatewayEvent(Model):
    op_code = Field(int, json_key="op")
    sequence = Field(int, json_key="s")
    name = Field(str, json_key="t")
    cache = None

class Ready(GatewayEvent):
    version = Field(int, json_key='v')
    user = Field(User)
    private_channels = ListField(Channel)
    guilds = ListField(Guild)
    session_id = Field(str)

class Resumed(GatewayEvent):
    pass

class InvalidSession(GatewayEvent):
    pass

class ChannelCreate(GatewayEvent):
    channel = Field(Channel, json_key="d")

    @property
    def guild(self):
        return self.cache.guilds.get(self.channel.guild_id)

class ChannelUpdate(GatewayEvent):
    channel = Field(Channel, json_key="d")

class ChannelDelete(GatewayEvent):
    channel = Field(Channel, json_key="d")
    
class ChannelPinsUpdate(GatewayEvent):
    guild_id = Field(Snowflake)
    channel_id = Field(Snowflake)
    last_pin_timestamp = Field(Timestamp)

    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)
        
    @property
    def channel(self):
        return self.cache.channels.get(self.channel_id)

class GuildCreate(GatewayEvent):
    guild = Field(Guild, json_key="d")

class GuildUpdate(GatewayEvent):
    guild = Field(Guild, json_key="d")
    
class GuildDelete(GatewayEvent):
    guild = Field(Guild, json_key="d")
    
class GuildBanAdd(GatewayEvent):
    guild_id = Field(Snowflake)
    user = Field(User)
    
    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)
    
class GuildBanRemove(GatewayEvent):
    guild_id = Field(Snowflake)
    user = Field(User)
    
    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)
        
class GuildEmojisUpdate(GatewayEvent):
    guild_id = Field(Snowflake)
    emojis = ListField(Emoji)
    
    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)
        
class GuildIntegrationsUpdate(GatewayEvent):
    guild_id = Field(Snowflake)

    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)
    
class GuildMemberAdd(GatewayEvent):
    member = Field(GuildMember, json_key="d")
    
    @property
    def guild(self):
        return self.cache.guilds.get(self.member.guild_id)
    
class GuildMemberRemove(GatewayEvent):
    guild_id = Field(Snowflake)
    user = Field(User)
    
    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)
        
class GuildMemberUpdate(GatewayEvent):
    guild_id = Field(Snowflake)
    user = Field(User)
    roles = ListField(Snowflake)
    nick = Field(str)
    
    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)
        
class GuildMembersChunk(GatewayEvent):
    guild_id = Field(Snowflake)
    members = ListField(GuildMember)

    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)
            
class GuildRoleCreate(GatewayEvent):
    guild_id = Field(Snowflake)
    role = Field(Role)

    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)
    
class GuildRoleUpdate(GatewayEvent):
    guild_id = Field(Snowflake)
    role = Field(Role)

    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)
            
class GuildRoleDelete(GatewayEvent):
    guild_id = Field(Snowflake)
    role = Field(Role)

    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)
            
class MessageCreate(GatewayEvent):
    message = Field(Message, json_key="d")
    
    @property
    def channel(self):
        return self.cache.channels.get(self.message.channel_id)

    @property
    def member(self):
        if self.message.is_guild:
            return self.guild.members.find(self.message.author.id)

    @property
    def guild(self):
        if self.message.is_guild:
            return self.cache.guilds.get(self.message.guild_id)
    
class MessageUpdate(GatewayEvent):
    message = Field(Message, json_key="d")
    
    @property
    def channel(self):
        return self.cache.channels.get(self.message.channel_id)

    @property
    def guild(self):
        if self.message.is_guild:
            return self.cache.guilds.get(self.message.guild_id)
    
class MessageDelete(GatewayEvent):
    id = Field(Snowflake)
    channel_id = Field(Snowflake)
    guild_id = Field(Snowflake)
    
    @property
    def channel(self):
        return self.cache.channels.get(self.channel_id)

    @property
    def guild(self):
        if self.message.is_guild:
            return self.cache.guilds.get(self.guild_id)
    
class MessageDeleteBulk(GatewayEvent):
    ids = ListField(Snowflake)
    channel_id = Field(Snowflake)
    guild_id = Field(Snowflake)
    
    @property
    def channel(self):
        return self.cache.channels.get(self.channel_id)

    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)

class MessageReactionAdd(GatewayEvent):
    user_id = Field(Snowflake)
    channel_id = Field(Snowflake)
    message_id = Field(Snowflake)
    guild_id = Field(Snowflake)
    emoji = Field(Emoji)
    
    @property
    def channel(self):
        return self.cache.guilds.get(self.channel_id)

    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)
    
class MessageReactionRemove(GatewayEvent):
    user_id = Field(Snowflake)
    channel_id = Field(Snowflake)
    message_id = Field(Snowflake)
    guild_id = Field(Snowflake)
    emoji = Field(Emoji)
    
    @property
    def channel(self):
        return self.cache.guilds.get(self.channel_id)

    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)
            
class MessageReactionRemoveAll(GatewayEvent):
    channel_id = Field(Snowflake)
    message_id = Field(Snowflake)
    guild_id = Field(Snowflake)
    
    @property
    def channel(self):
        return self.cache.guilds.get(self.channel_id)

    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)

class PresenceUpdate(GatewayEvent):
    pass
    
class TypingStart(GatewayEvent):
    guild_id = Field(Snowflake)
    channel_id = Field(Snowflake)
    user_id = Field(Snowflake)
    unix_time = Field(int, json_key="timestamp")
    
    @property
    def timestamp(self):
        return Timestamp.from_unix(self.unix_time)
    
    @property
    def user(self):
        return self.cache.users.get(self.user_id)
    
    @property
    def channel(self):
        return self.cache.guilds.get(self.channel_id)

    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)
        
class UserUpdate(GatewayEvent):
    user = Field(User, json_key="d")

class VoiceStateUpdate(GatewayEvent):
    voice_state = Field(VoiceState, json_key="d")

    @property
    def connected(self):
        return False if self.channel is None else True

    @property
    def user(self):
        return self.cache.users.get(self.voice_state.user_id)
    
    @property
    def channel(self):
        return self.cache.channels.get(self.voice_state.channel_id)

    @property
    def guild(self):
        return self.cache.guilds.get(self.voice_state.guild_id)
    
class VoiceServerUpdate(GatewayEvent):
    pass
    
class WebhooksUpdate(GatewayEvent):
    guild_id = Field(Snowflake)
    message_id = Field(Snowflake)
    
    @property
    def channel(self):
        return self.cache.guilds.get(self.channel.id)

    @property
    def guild(self):
        return self.cache.guilds.get(self.guild_id)
