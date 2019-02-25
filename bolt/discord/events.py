from bolt.discord.models import Embed, User, Message
from bolt.discord.models.message import Reaction
from bolt.discord.models.guild import Guild, GuildMember
from bolt.discord.models.channel import Channel, ChannelType



from enum import Enum, auto
import json
import gevent
import logging

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
        handler = getattr(self, "on_" + event.typ.name.lower())
        handler(event)

    def on_ready(self, event):
        event_data = event._raw_data_
        for guild in event_data['guilds']:
            self.cache.guilds[guild['id']] = Guild.marshal(guild)

        self.cache.user = User.marshal(event_data['user'])
        event.user = self.cache.user
        event.session_id = event_data['session_id']

    #
    # Guild Handlers
    #

    def on_guild_create(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds[event_data['id']]
        guild.remarshal(event_data)
        event.guild = guild

        for member in event.guild.members:
            self.cache.users[str(member.user.id)] = member.user

    def on_guild_update(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds[event_data['id']]
        guild.remarshal(event_data)
        event.guild = guild

    def on_guild_delete(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds[event_data['id']]
        del self.cache.guilds[event_data['id']]
        event.guild = guild

    def on_guild_ban_add(self, event):
        event_data = event._raw_data_
        guild_id = event_data['guild_id']
        guild = self.cache.guilds[guild_id]
        banned_member = None

        for member in guild.members:
            if member.user.id == event_data['user']['id']:
                banned_member = member
                guild.members.remove(member)

        event.guild = guild
        event.member = banned_member

    def on_guild_ban_remove(self, event):
        event_data = event._raw_data_

        guild_id = event_data['guild_id']
        user_id = event_data['user']['id']

        try:
            user = self.cache.users[event_data['user']['id']]
        except KeyError as e:
            user = User.marshal(event_data['user'])
            self.cache.users[user.id] = user

        event.guild = self.cache.guilds[guild_id]
        event.user = user

    def on_guild_emojis_update(self, event):
        event_data = event._raw_data_

    def on_guild_integrations_update(self, event):
        event_data = event._raw_data_

    def on_guild_member_add(self, event):
        """
            Create new guild member
            Append guild member to existing guild
            Upsert new member in user cache
            Add Guild and User info to event object
        """
        event_data = event._raw_data_
        guild_id = event_data['guild_id']
        user_id = event_data['user']['id']

        guild = self.cache.guilds[guild_id]
        member = GuildMember.marshal(event_data)
        guild.members.append(member)

        if not self.cache.users.get(member.user.id):
            self.cache.users[str(member.user.id)] = member.user

        event.guild = guild
        event.member = member

    def on_guild_member_remove(self, event):
        event_data = event._raw_data_

        guild_id = event_data['guild_id']
        user_id = event_data['user']['id']

        guild = self.cache.guilds[guild_id]
        removed_member = None

        for index, member in enumerate(guild.members):
            if member.user.id == user_id:
                removed_member = guild.members.pop(index)
                break

        event.member = removed_member
        event.guild = guild

    def on_guild_member_update(self, event):
        event_data = event._raw_data_

    def on_guild_members_chunk(self, event):
        event_data = event._raw_data_

    def on_guild_role_create(self, event):
        event_data = event._raw_data_

    def on_guild_role_update(self, event):
        event_data = event._raw_data_

    def on_guild_role_delete(self, event):
        event_data = event._raw_data_

    #
    # Channel Handlers
    #

    def on_channel_create(self, event):
        event_data = event._raw_data_

        channel = Channel.marshal(event_data)
        if channel.type in [ChannelType.GUILD_TEXT, ChannelType.GUILD_VOICE, ChannelType.GUILD_CATEGORY]:
            guild = self.cache.guilds[str(channel.guild_id)]
            guild.channels.append(channel)
            event.guild = guild

        event.channel = channel

    def on_channel_update(self, event):
        event_data = event._raw_data_

    def on_channel_delete(self, event):
        event_data = event._raw_data_

        if ChannelType(event_data['type']) in [ChannelType.GUILD_TEXT, ChannelType.GUILD_VOICE, ChannelType.GUILD_CATEGORY]:
            guild = self.cache.guilds[str(event_data['guild_id'])]
            removed_channel = None

            for index, channel in enumerate(guild.channels):
                if channel.id == event_data['id']:
                    removed_channel = guild.channels.pop(index)

            event.channel = removed_channel


    def on_channel_pins_update(self, event):
        event_data = event._raw_data_

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
        event_data = event._raw_data_

    def on_message_reaction_add(self, event):
        event_data = event._raw_data_
        message = Reaction.marshal(event_data)
        event.message = message

    def on_message_reaction_remove(self, event):
        event_data = event._raw_data_

    def on_message_reaction_remove_all(self, event):
        event_data = event._raw_data_

    #
    # Misc Handlers
    #

    def on_presence_update(self, event):
        event_data = event._raw_data_

    def on_typing_start(self, event):
        event_data = event._raw_data_

    def on_user_update(self, event):
        event_data = event._raw_data_

    def on_voice_state_update(self, event):
        event_data = event._raw_data_

    def on_voice_server_update(self, event):
        event_data = event._raw_data_

    def on_webhooks_update(self, event):
        event_data = event._raw_data_




"""
    ✔   unknown user joins guild
    ✔   user joins guild
    ✔   user leaves guild
    ✔   user kicked from guild
    ✔   user banned from guild
    ✔   user unbanned from guild
    unknown user unbanned from guild
    guild roles updated
    guild emojis add
    guild emojis remove
    guild emojis update

    ✔   channel created
    ✔   channel deleted
    channel permissions override
    channel updated

    typing start
    pressence update

    unknown user creates DM with you
    user creates DM with you
    message deleted from channel
    message edited from channel
    message pinned in channel
    message created in channel
    user adds react to message
    user removes reaction from message
    all reactions cleared from message

    user moved voice channels by admin
    user joins voice channel
    user leaves voice channel
    user mutes mic
    user mutes speakers
    user mutes both
    user unmutes mic
    user unmutes speakers
    user unmutes both
    user global muted by admin
    user global unmuted by admin
"""
