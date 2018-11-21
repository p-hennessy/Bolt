"""
    This module provides a class that implements the full spec of the Discord API
    https://discordapp.com/developers/docs/

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it under the terms of the GNU
        General Public License v3; as published by the Free Software Foundation
"""
import ujson as json
import gevent
import requests
import time
import logging


def rate_limit():
    def decorate(callback):
        callback.reset = time.time()

        def wrapper(self, *args, **kwargs):
            # Check if there is a timeout
            if time.time() < callback.reset:
                delay = callback.reset - time.time()
                self.logger.warning(f"Rate limited, sleeping for {delay} seconds")
                gevent.sleep(delay)

            # Call real method
            response = callback(self, *args, **kwargs)

            # Look for rate limit headers
            remaining = int(response.headers.get('X-RateLimit-Remaining', 1))
            reset = float(response.headers.get('X-RateLimit-Reset', time.time()))

            # We will have to wait on next request until reset
            if remaining == 0:
                callback.reset = reset

            response.raise_for_status()

            if response.text:
                return response.json()

        return wrapper
    return decorate


class API():
    def __init__(self, token):
        self.auth_headers = {
            "authorization": "Bot " + token,
            "Content-Type": 'application/json'
        }
        self.base_url = "https://discordapp.com/api"
        self.logger = logging.getLogger(__name__)

    # Gateway methods
    @rate_limit()
    def get_gateway(self):
        return requests.get(
            f"{self.base_url}/gateway",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_gateway_bot(self):
        return requests.get(
            f"{self.base_url}/gateway/bot",
            headers=self.auth_headers
        )

    # Channel methods
    @rate_limit()
    def get_channel(self, channel_id):
        return requests.get(
            f"{self.base_url}/channels/{channel_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def modify_channel(self, channel_id, **kwargs):
        return requests.put(
            f"{self.base_url}/channels/{channel_id}",
            headers=self.auth_headers,
            data=json.dumps(kwargs)
        )

    @rate_limit()
    def delete_channel(self, channel_id):
        return requests.delete(
            f"{self.base_url}/channels/{channel_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_channel_messages(self, channel_id, **kwargs):
        return requests.get(
            f"{self.base_url}/channels/{channel_id}/messages",
            headers=self.auth_headers,
            params=kwargs
        )

    @rate_limit()
    def get_channel_message(self, channel_id, message_id):
        return requests.get(
            f"{self.base_url}/channels/{channel_id}/messages/{message_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def create_message(self, channel_id, message_data, files=None):
        if isinstance(message_data, dict):
            message_data = json.dumps(message_data)

        return requests.post(
            f"{self.base_url}/channels/{channel_id}/messages",
            data=message_data,
            files=files,
            headers=self.auth_headers
        )

    @rate_limit()
    def create_reaction(self, channel_id, message_id, emoji):
        return requests.put(
            f"{self.base_url}/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
            headers=self.auth_headers
        )

    @rate_limit()
    def delete_own_reaction(self, channel_id, message_id, emoji):
        return requests.delete(
            f"{self.base_url}/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
            headers=self.auth_headers
        )

    @rate_limit()
    def delete_user_reaction(self, channel_id, message_id, emoji, user_id):
        return requests.delete(
            f"{self.base_url}/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def delete_all_reactions(self, channel_id, message_id):
        return requests.delete(
            f"{self.base_url}/channels/{channel_id}/messages/{message_id}/reactions",
            headers=self.auth_headers
        )

    @rate_limit()
    def edit_message(self, channel_id, message_id, **kwargs):
        return requests.patch(
            f"{self.base_url}/channels/{channel_id}/messages/{message_id}",
            headers=self.auth_headers,
            data=json.dumps(kwargs)
        )

    @rate_limit()
    def delete_message(self, channel_id, message_id):
        return requests.delete(
            f"{self.base_url}/channels/{channel_id}/messages/{message_id}",
            headers=self.auth_headers,
        )

    @rate_limit()
    def bulk_delete_messages(self, channel_id, **kwargs):
        return requests.delete(
            f"{self.base_url}/channels/{channel_id}/messages/bulk-delete",
            headers=self.auth_headers,
            data=json.dumps(kwargs)
        )

    @rate_limit()
    def get_channel_invites(self, channel_id):
        return requests.delete(
            f"{self.base_url}/channels/{channel_id}/invites",
            headers=self.auth_headers
        )

    @rate_limit()
    def create_channel_invite(self, channel_id, **kwargs):
        return requests.post(
            f"{self.base_url}/channels/{channel_id}/invites",
            headers=self.auth_headers,
            data=json.dumps(kwargs)
        )

    @rate_limit()
    def trigger_typing(self, channel_id):
        return requests.post(
            f"{self.base_url}/channels/{channel_id}/typing",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_pinned_messsages(self, channel_id):
        return requests.get(
            f"{self.base_url}/channels/{channel_id}/pins",
            headers=self.auth_headers
        )

    @rate_limit()
    def add_pinned_channel_message(self, channel_id, message_id):
        return requests.put(
            f"{self.base_url}/channels/{channel_id}/pins/{message_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def delete_pinned_channel_message(self, channel_id, message_id):
        return requests.delete(
            f"{self.base_url}/channels/{channel_id}/pins/{message_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def add_recipient_group_dm(self, channel_id, user_id, **kwargs):
        return requests.put(
            f"{self.base_url}/channels/{channel_id}/recipients/{user_id}",
            headers=self.auth_headers,
            data=json.dumps(kwargs)
        )

    @rate_limit()
    def remove_recipient_group_dm(self, channel_id, user_id):
        return requests.delete(
            f"{self.base_url}/channels/{channel_id}/recipients/{user_id}",
            headers=self.auth_headers,
        )

    # User Methods
    @rate_limit()
    def get_current_user(self):
        return requests.get(
            f"{self.base_url}/users/@me",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_user(self, user_id):
        return requests.get(
            f"{self.base_url}/users/{user_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def modify_current_user(self, username, avatar_data=None):
        return requests.patch(
            f"{self.base_url}/users/@me",
            headers=self.auth_headers,
            data=json.dumps({"username": username, "avatar": avatar_data})
        )

    @rate_limit()
    def get_current_user_guilds(self):
        return requests.get(
            f"{self.base_url}/users/@me/guilds",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_user_profile(self, user_id):
        return requests.get(
            f"{self.base_url}/users/{user_id}/profile",
            headers=self.auth_headers
        )

    @rate_limit()
    def leave_guild(self, guild_id):
        return requests.delete(
            f"{self.base_url}/users/@me/guilds/{guild_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_user_dms(self):
        return requests.get(
            f"{self.base_url}/users/@me/channels",
            headers=self.auth_headers
        )

    @rate_limit()
    def create_dm(self, user_id):
        return requests.post(
            f"{self.base_url}/users/@me/channels",
            headers=self.auth_headers,
            data=json.dumps({"recipient_id": user_id})
        )

    @rate_limit()
    def get_user_connections(self):
        return requests.get(
            f"{self.base_url}/users/@me/connections",
            headers=self.auth_headers,
        )

    # Guild Methods
    @rate_limit()
    def create_guild(self, **kwargs):
        return requests.post(
            f"{self.base_url}/guilds",
            headers=self.auth_headers,
            data=json.dumps(kwargs)
        )

    @rate_limit()
    def get_guild(self, guild_id):
        return requests.get(
            f"{self.base_url}/guilds/{guild_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def modify_guild(self, guild_id, **kwargs):
        return requests.patch(
            f"{self.base_url}/guilds/{guild_id}",
            headers=self.auth_headers,
            data=json.dumps(kwargs)
        )

    @rate_limit()
    def delete_guild(self, guild_id):
        return requests.delete(
            f"{self.base_url}/guilds/{guild_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_guild_channels(self, guild_id):
        return requests.get(
            f"{self.base_url}/guilds/{guild_id}/channels",
            headers=self.auth_headers
        )

    @rate_limit()
    def create_guild_channel(self, guild_id, name, **kwargs):
        data = {
            "name": name
        }
        data.update(**kwargs)

        return requests.post(
            f"{self.base_url}/guilds/{guild_id}/channels",
            data=json.dumps(data),
            headers=self.auth_headers
        )

    @rate_limit()
    def modify_guild_channel_positions(self, guild_id):
        raise NotImplemented

    @rate_limit()
    def get_guild_member(self, guild_id, user_id):
        return requests.get(
            f"{self.base_url}/guilds/{guild_id}/members/{user_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def list_guild_members(self, guild_id, **kwargs):
        return requests.get(
            f"{self.base_url}/guilds/{guild_id}/members",
            headers=self.auth_headers,
            params=kwargs
        )

    @rate_limit()
    def add_guild_members(self, guild_id, user_id):
        raise NotImplemented

    @rate_limit()
    def modify_guild_member(self, guild_id, user_id, **kwargs):
        return requests.patch(
            f"{self.base_url}/guilds/{guild_id}/members/{user_id}",
            headers=self.auth_headers,
            data=json.dumps(kwargs)
        )

    @rate_limit()
    def modify_current_user_nick(self, guild_id, nick):
        return requests.patch(
            f"{self.base_url}/guilds/{guild_id}/members/@me/nick",
            headers=self.auth_headers,
            data=json.dumps({"nick": nick})
        )

    @rate_limit()
    def add_guild_member_role(self, guild_id, user_id, role_id):
        raise NotImplemented

    @rate_limit()
    def remove_guild_member_role(self, guild_id, user_id, role_id):
        raise NotImplemented

    @rate_limit()
    def remove_guild_member(self, guild_id, user_id):
        raise NotImplemented

    @rate_limit()
    def get_guild_bans(self, guild_id):
        raise NotImplemented

    @rate_limit()
    def create_guild_ban(self, guild_id, user_id):
        raise NotImplemented

    @rate_limit()
    def delete_guild_ban(self, guild_id, user_id):
        raise NotImplemented

    @rate_limit()
    def get_guild_roles(self, guild_id):
        return requests.get(
            f"{self.base_url}/guilds/{guild_id}/roles",
            headers=self.auth_headers
        )

    @rate_limit()
    def create_guild_role(self, guild_id, **kwargs):
        raise NotImplemented

    @rate_limit()
    def modify_guild_role_positions(self, guild_id, **kwargs):
        raise NotImplemented

    @rate_limit()
    def modify_guild_role(self, guild_id, role_id, **kwargs):
        raise NotImplemented

    @rate_limit()
    def delete_guild_role(self, guild_id, role_id):
        raise NotImplemented

    @rate_limit()
    def get_guild_prune_count(self, guild_id):
        raise NotImplemented

    @rate_limit()
    def begin_guild_prune(self, guild_id):
        raise NotImplemented

    @rate_limit()
    def get_guild_voice_region(self, guild_id):
        raise NotImplemented

    @rate_limit()
    def get_guild_invites(self, guild_id):
        raise NotImplemented

    @rate_limit()
    def get_guild_integrations(self, guild_id):
        raise NotImplemented

    @rate_limit()
    def create_guild_integrations(self, guild_id):
        raise NotImplemented

    @rate_limit()
    def modify_guild_integrations(self, guild_id, integration_id):
        raise NotImplemented

    @rate_limit()
    def delete_guild_integrations(self, guild_id, integration_id):
        raise NotImplemented

    @rate_limit()
    def sync_guild_integration(self, guild_id, integration_id):
        raise NotImplemented

    @rate_limit()
    def get_guild_embed(self, guild_id):
        raise NotImplemented

    @rate_limit()
    def modify_guild_embed(self, guild_id):
        raise NotImplemented

    @rate_limit()
    def accept_invite(self, invite_code):
        return requests.post(
            f"{self.base_url}/invites/{invite_code}",
            headers=self.auth_headers
        )
