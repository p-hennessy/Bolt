from bolt.discord.models import User, Message
from bolt.discord.models.base import Timestamp
from bolt.discord.models.message import Reaction
from bolt.discord.models.guild import Guild, GuildMember, VoiceState, Role
from bolt.discord.models.emoji import Emoji
from bolt.discord.models.channel import Channel, ChannelType

from enum import Enum, auto
import gevent
import logging
from copy import deepcopy


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


class Event():
    """
        Incomplete event object
        Expect handlers to add rich model objects onto these
    """
    def __init__(self, opcode, sequence, event_name, data):
        self.op_code = opcode
        self.sequence = sequence
        self.name = event_name
        self.typ = getattr(Events, str(event_name), None)
        self._raw_data_ = data

    @classmethod
    def marshal(cls, data):
        return cls(data['op'], data['s'], data['t'], data['d'])


class EventHandler():
    def __init__(self, bot, cache):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.cache = cache

    def dispatch(self, event, subscriptions):
        for subscription in subscriptions:
            if subscription.event == event.typ:
                self.logger.debug(
                    f"Dispatching \"{event.typ.name}\" to "
                    f"{subscription.callback.__self__.__module__}."
                    f"{subscription.callback.__self__.__class__.__name__}."
                    f"{subscription.callback.__name__}"
                )
                self.bot.queue.put((subscription.callback, [event], {}))
            gevent.sleep(0)

    def handle(self, event):
        # Dynamically find correct event handler based on name
        self.logger.debug(f"Handling {event.typ.name.lower()}")
        handler = getattr(self, "on_" + event.typ.name.lower())
        handler(event)

    def on_ready(self, event):
        event_data = event._raw_data_
        for guild in event_data['guilds']:
            new_guild = Guild.marshal(guild)
            self.cache.guilds.upsert(new_guild)

        self.cache.user = User.marshal(event_data['user'])
        event.user = self.cache.user
        event.session_id = event_data['session_id']

    #
    # Guild Handlers
    #

    def on_guild_create(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds.find(id=event_data['id'])
        guild.remarshal(event_data)
        event.guild = guild

        # for member in guild.members:
        #     member.api = self.bot.api
        #     member.guild_id = guild.id
        # for role in guild.roles:
        #     role.api = self.bot.api

        for member in event.guild.members:
            self.cache.users.upsert(member.user)

    def on_guild_update(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds.find(id=event_data['id'])
        guild.remarshal(event_data)
        event.guild = deepcopy(guild)

    def on_guild_delete(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds.find(id=event_data['id'])
        event.guild = deepcopy(guild)
        self.cache.guilds.remove(guild)

    def on_guild_ban_add(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds.find(id=event_data['id'])
        banned_member = None

        for member in guild.members:
            if member.user.id == event_data['user']['id']:
                banned_member = member
                guild.members.remove(member)

        event.guild = deepcopy(guild)
        event.member = deepcopy(banned_member)

    def on_guild_ban_remove(self, event):
        event_data = event._raw_data_

        guild = self.cache.guilds.find(id=event_data['id'])
        user = self.cache.users.find(event_data['user']['id'])

        if user is None:
            user = User.marshal(event_data['user'])
            self.cache.users.upsert(user)

        event.guild = deepcopy(guild)
        event.user = deepcopy(user)

    def on_guild_emojis_update(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds.find(id=event_data['guild_id'])
        guild.emojis = []

        for emoji in event_data['emojis']:
            new_emoji = Emoji.marshal(emoji)
            guild.emojis.append(new_emoji)

        event.guild = deepcopy(guild)

    def on_guild_integrations_update(self, event):
        return NotImplemented

    def on_guild_member_add(self, event):
        """
            Create new guild member
            Append guild member to existing guild
            Upsert new member in user cache
            Add Guild and User info to event object
        """
        event_data = event._raw_data_
        guild = self.cache.guilds.find(id=event_data['id'])
        member = GuildMember.marshal(event_data)
        guild.members.upsert(member)

        if not self.cache.users.find(id=member.user.id):
            self.cache.users.upsert(member.user)

        event.guild = deepcopy(guild)
        event.member = deepcopy(member)

    def on_guild_member_remove(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds.find(id=event_data['guild_id'])
        member = guild.members.find(id=event_data['user']['id'])
        event.member = deepcopy(member)
        event.guild = deepcopy(guild)
        guild.members.remove(member)

    def on_guild_member_update(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds.find(id=event_data['guild_id'])
        member = guild.members.find(id=event_data['user']['id'])
        member.remarshal(event_data)
        event.guild = deepcopy(guild)
        event.member = deepcopy(member)

    def on_guild_members_chunk(self, event):
        return NotImplemented

    def on_guild_role_create(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds.find(id=event_data['guild_id'])
        role = Role.marshal(event_data['role'])
        guild.roles.append(role)
        event.role = deepcopy(role)
        event.guild = deepcopy(guild)

    def on_guild_role_update(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds.find(id=event_data['guild_id'])
        role = guild.roles.find(id=event_data['role']['id'])
        role.remarshal(event_data['role'])
        event.role = deepcopy(role)
        event.guild = deepcopy(guild)

    def on_guild_role_delete(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds.find(id=event_data['guild_id'])
        role = guild.roles.find(id=event_data['role_id'])
        event.role = deepcopy(role)
        event.guild = deepcopy(role)
        guild.roles.remove(role)
    #
    # Channel Handlers
    #

    def on_channel_create(self, event):
        event_data = event._raw_data_
        channel = Channel.marshal(event_data)
        if channel.type in [ChannelType.GUILD_TEXT, ChannelType.GUILD_VOICE, ChannelType.GUILD_CATEGORY]:
            guild = self.cache.guilds.find(id=channel.guild_id)
            guild.channels.append(channel)
            event.guild = deepcopy(guild)
            event.channel = deepcopy(channel)
        elif channel.type in [ChannelType.DM, ChannelType.GROUP_DM]:
            self.cache.private_channels.append(channel)
            event.channel = deepcopy(channel)

    def on_channel_update(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds.find(id=event_data['guild_id'])
        existing = guild.channels.find(id=event_data['id'])
        existing.remarshal(event_data)
        event.guild = deepcopy(guild)
        event.channel = deepcopy(existing)

    def on_channel_delete(self, event):
        event_data = event._raw_data_
        channel_type = ChannelType(event_data['type'])
        if channel_type in [ChannelType.GUILD_TEXT, ChannelType.GUILD_VOICE, ChannelType.GUILD_CATEGORY]:
            guild = self.cache.guilds.find(id=event_data['guild_id'])
            channel = guild.channels.find(id=event_data['id'])
            event.guild = deepcopy(guild)
            event.channel = deepcopy(channel)
            guild.channels.remove(channel)
        elif channel_type in [ChannelType.DM, ChannelType.GROUP_DM]:
            channel = self.cache.private_channels.find(id=event_data['id'])
            event.channel = deepcopy(channel)
            self.cache.private_channels.remove(channel)

    def on_channel_pins_update(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds.find(id=event_data['guild_id'])
        existing = guild.channels.find(id=event_data['channel_id'])
        existing.last_pin_timestamp = Timestamp(event_data['last_pin_timestamp'])
        event.guild = deepcopy(guild)
        event.channel = deepcopy(existing)

    #
    # Message Handlers
    #

    def on_message_create(self, event):
        """
            Required for the Command system to function
        """
        event_data = event._raw_data_
        message = Message.marshal(event_data)
        event.message = message

    def on_message_update(self, event):
        event_data = event._raw_data_
        message = Message.marshal(event_data)
        event.message = message

    def on_message_delete(self, event):
        event_data = event._raw_data_
        message = Message.marshal(event_data)
        event.message = message

    def on_message_delete_bulk(self, event):
        return NotImplemented

    def on_message_reaction_add(self, event):
        event_data = event._raw_data_
        message = Reaction.marshal(event_data)
        event.message = message

    def on_message_reaction_remove(self, event):
        event_data = event._raw_data_
        message = Reaction.marshal(event_data)
        event.message = message

    def on_message_reaction_remove_all(self, event):
        event_data = event._raw_data_
        message = Reaction.marshal(event_data)
        event.message = message

    #
    # Misc Handlers
    #

    def on_presence_update(self, event):
        event_data = event._raw_data_
        user = self.cache.users.find(id=event_data['user']['id'])
        user.status = event_data['status']
        event.user = deepcopy(user)

    def on_typing_start(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds.find(id=event_data['guild_id'])
        member = guild.members.find(event_data['user_id'])
        channel = guild.channels.find(event_data['channel_id'])
        event.member = deepcopy(member)
        event.channel = deepcopy(channel)
        event.guild = deepcopy(guild)
        event.timestamp = Timestamp.from_unix(event_data['timestamp'])

    def on_user_update(self, event):
        return NotImplemented

    def on_voice_state_update(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds.find(id=event_data['guild_id'])
        old_state = guild.voice_states.find(user_id=event_data['user_id'])
        guild.voice_states.remove(old_state)
        new_state = VoiceState.marshal(event_data)
        guild.voice_states.upsert(new_state)

    def on_voice_server_update(self, event):
        return NotImplemented

    def on_webhooks_update(self, event):
        return NotImplemented
