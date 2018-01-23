"""
    Description:
        Where the magic happens
        All events from the web socket are funneled through these functions

    Contributors:
        - Patrick Hennessy
"""
import re
import gevent

from arcbot.discord.models import *
from arcbot.discord.events import Events

class Handlers():
    def __init__(self, bot):
        self.bot = bot

        self.bot.guilds = {}
        self.bot.channels = {}

        self.bot.events.subscribe(Events.READY, self.handle_gateway_ready)
        self.bot.events.subscribe(Events.MESSAGE_CREATE, self.handle_gateway_message)
        self.bot.events.subscribe(Events.CHANNEL_CREATE, self.handle_null)
        self.bot.events.subscribe(Events.CHANNEL_UPDATE, self.handle_null)
        self.bot.events.subscribe(Events.CHANNEL_DELETE, self.handle_null)
        self.bot.events.subscribe(Events.CHANNEL_PINS_UPDATE, self.handle_null)
        self.bot.events.subscribe(Events.GUILD_CREATE, self.handle_guild_create)
        self.bot.events.subscribe(Events.GUILD_UPDATE, self.handle_null)
        self.bot.events.subscribe(Events.GUILD_DELETE, self.handle_null)
        self.bot.events.subscribe(Events.GUILD_BAN_ADD, self.handle_null)
        self.bot.events.subscribe(Events.GUILD_BAN_REMOVE, self.handle_null)
        self.bot.events.subscribe(Events.GUILD_EMOJIS_UPDATE, self.handle_null)
        self.bot.events.subscribe(Events.GUILD_INTEGRATIONS_UPDATE, self.handle_null)
        self.bot.events.subscribe(Events.GUILD_MEMBER_ADD, self.handle_null)
        self.bot.events.subscribe(Events.GUILD_MEMBER_REMOVE, self.handle_null)
        self.bot.events.subscribe(Events.GUILD_MEMBERS_CHUNK, self.handle_null)
        self.bot.events.subscribe(Events.GUILD_ROLE_CREATE, self.handle_null)
        self.bot.events.subscribe(Events.GUILD_ROLE_UPDATE, self.handle_null)
        self.bot.events.subscribe(Events.GUILD_ROLE_DELETE, self.handle_null)
        self.bot.events.subscribe(Events.PRESENCE_UPDATE, self.handle_null)
        self.bot.events.subscribe(Events.USER_UPDATE, self.handle_null)
        self.bot.events.subscribe(Events.VOICE_STATE_UPDATE, self.handle_voice_state_update)
        self.bot.events.subscribe(Events.VOICE_SERVER_UPDATE, self.handle_null)

    def handle_null(self, event):
        pass

    def handle_gateway_ready(self, event):
        self.bot.user_id = event['user']['id']
        self.bot.session_id = event['session_id']

    def handle_gateway_message(self, event):
        def iter_commands():
            for plugin in self.bot.plugins:
                if not plugin.enabled:
                    continue

                for command in plugin.commands:
                    yield command

        def iter_pre_command_hooks():
            for plugin in self.bot.plugins:
                if not plugin.enabled:
                    continue

                for hook in plugin.pre_command_hooks:
                    yield hook

        message = Message.from_json(event)

        if message.author.id == self.bot.user_id:
            return

        for command in iter_commands():
            if command.matches(message.content):
                args, kwargs = command.parse(message.content)

                message.args = args
                message.kwargs = kwargs

                for hook in iter_pre_command_hooks():
                    if hook(command, message) is False:
                        return

                self.bot.queue.put((command.invoke, [message], {}))
                gevent.sleep(0)

    def handle_channel_create(self, event):
        raise NotImplemented

    def handle_channel_create(self, event):
        raise NotImplemented

    def handle_channel_update(self, event):
        raise NotImplemented

    def handle_channel_delete(self, event):
        raise NotImplemented

    def handle_channel_pins_update(self, event):
        raise NotImplemented

    def handle_guild_create(self, event):
        guild = Guild.from_json(event)
        self.bot.guilds[event.get("id")] = guild

        for channel in guild.channels:
            self.bot.channels[channel.id] = channel

    def handle_guild_update(self, event):
        self.bot.guilds[event.get("id")].update(event)

    def handle_guild_delete(self, event):
        del self.bot.guilds[event.get("id")]

    def handle_guild_ban_add(self, event):
        raise NotImplemented

    def handle_guild_ban_remove(self, event):
        raise NotImplemented

    def handle_guild_emojis_update(self, event):
        raise NotImplemented

    def handle_guild_integrations_update(self, event):
        raise NotImplemented

    def handle_guild_member_add(self, event):
        raise NotImplemented

    def handle_guild_member_remove(self, event):
        raise NotImplemented

    def handle_guild_members_chunk(self, event):
        raise NotImplemented

    def handle_guild_role_create(self, event):
        raise NotImplemented

    def handle_guild_role_update(self, event):
        raise NotImplemented

    def handle_guild_role_delete(self, event):
        raise NotImplemented

    def handle_pressence_update(self, event):
        raise NotImplemented

    def handle_user_update(self, event):
        raise NotImplemented

    def handle_voice_server_update(self, event):
        raise NotImplemented

    def handle_voice_state_update(self, event):
        raise NotImplemented
