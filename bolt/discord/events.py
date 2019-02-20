from bolt.discord.models import Channel, Embed, Guild, User, Message

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

    def on_guild_create(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds[event_data['id']]
        guild.remarshal(event_data)
        event.guild = guild

    def on_guild_update(self, event):
        event_data = event._raw_data_
        guild = self.cache.guilds[event_data['id']]
        guild.remarshal(event_data)
        event.guild = guild

    def on_guild_delete(self, event):
        pass

    def on_guild_ban_add(self, event):
        pass

    def on_guild_ban_remove(self, event):
        pass

    def on_guild_emojis_update(self, event):
        pass

    def on_guild_integrations_update(self, event):
        pass

    def on_guild_member_add(self, event):
        pass

    def on_guild_member_remove(self, event):
        pass

    def on_guild_member_update(self, event):
        pass

    def on_guild_members_chunk(self, event):
        pass

    def on_guild_role_create(self, event):
        pass

    def on_guild_role_update(self, event):
        pass

    def on_guild_role_delete(self, event):
        pass

    def on_channel_create(self, event):
        pass

    def on_channel_update(self, event):
        pass

    def on_channel_delete(self, event):
        pass

    def on_channel_pins_update(self, event):
        pass

    def on_message_create(self, event):
        event_data = event._raw_data_
        message = Message.marshal(event_data)
        event.message = message

    def on_message_update(self, event):
        event_data = event._raw_data_
        message = Message.marshal(event_data)
        event.message = message

    def on_message_delete(self, event):
        pass

    def on_message_delete_bulk(self, event):
        pass

    def on_message_reaction_add(self, event):
        pass

    def on_message_reaction_remove(self, event):
        pass

    def on_message_reaction_remove_all(self, event):
        pass

    def on_presence_update(self, event):
        pass

    def on_typing_start(self, event):
        pass

    def on_user_update(self, event):
        pass

    def on_voice_state_update(self, event):
        pass

    def on_voice_server_update(self, event):
        pass

    def on_webhooks_update(self, event):
        pass
