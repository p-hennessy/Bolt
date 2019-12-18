"""
    This module provides a class that implements the full spec of the Discord API
    https://discordapp.com/developers/docs/

    Contributors:
        - Patrick Hennessy
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
            # Check if there is an existing timeout from previous calls
            if time.time() < callback.reset:
                delay = callback.reset - time.time()
                self.logger.warning(f"Rate limited, sleeping for {delay} seconds")
                gevent.sleep(delay)

            retries_remaining = 3
            while retries_remaining > 0:
                if retries_remaining == 0:
                    raise Exception("Exceeded max retries for request.")

                # Call real method
                response = callback(self, *args, **kwargs)

                # Look for rate limit headers
                remaining = int(response.headers.get('X-RateLimit-Remaining', 1))
                reset = float(response.headers.get('X-RateLimit-Reset', time.time()))

                # We will have to wait on next request until reset
                if remaining == 0:
                    callback.reset = reset

                # Check if this request is the timeout. Can happen when reconnecting the bot a lot
                if response.status_code == 429:
                    delay = callback.reset - time.time()
                    self.logger.warning(f"Rate limited, sleeping for {delay} seconds")
                    gevent.sleep(delay)
                    retries_remaining -= 1
                    continue
                else:
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
        return requests.post(
            f"{self.base_url}/channels/{channel_id}/messages",
            data=json.dumps(message_data),
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
    def edit_message(self, channel_id, message_id, message_data):
        return requests.patch(
            f"{self.base_url}/channels/{channel_id}/messages/{message_id}",
            headers=self.auth_headers,
            data=json.dumps(message_data)
        )

    @rate_limit()
    def delete_message(self, channel_id, message_id):
        return requests.delete(
            f"{self.base_url}/channels/{channel_id}/messages/{message_id}",
            headers=self.auth_headers
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
    def get_pinned_messages(self, channel_id):
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
            data=json.dumps(kwargs)
        )

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
        return requests.put(
            f"{self.base_url}/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def remove_guild_member_role(self, guild_id, user_id, role_id):
        return requests.delete(
            f"{self.base_url}/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def remove_guild_member(self, guild_id, user_id):
        return requests.delete(
            f"{self.base_url}/guilds/{guild_id}/members/{user_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_guild_bans(self, guild_id):
        return requests.get(
            f"{self.base_url}/guilds/{guild_id}/bans",
            headers=self.auth_headers
        )

    @rate_limit()
    def create_guild_ban(self, guild_id, user_id, delete_message_days=0, reason="No reason given"):
        return requests.put(
            f"{self.base_url}/guilds/{guild_id}/bans/{user_id}",
            headers=self.auth_headers,
            data=json.dumps({"delete-message-days": delete_message_days, "reason": reason})
        )

    @rate_limit()
    def delete_guild_ban(self, guild_id, user_id):
        return requests.delete(
            f"{self.base_url}/guilds/{guild_id}/bans/{user_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_guild_roles(self, guild_id):
        return requests.get(
            f"{self.base_url}/guilds/{guild_id}/roles",
            headers=self.auth_headers
        )

    @rate_limit()
    def create_guild_role(self, guild_id, name, permissions=0, color=0, hoist=False, mentionable=False):
        role_data = {
            "name": name,
            "permissions": permissions,
            "color": color,
            "hoist": hoist,
            "mentionable": mentionable
        }

        return requests.post(
            f"{self.base_url}/guilds/{guild_id}/roles",
            headers=self.auth_headers,
            data=json.dumps(role_data)
        )

    @rate_limit()
    def modify_guild_role_positions(self, guild_id, positions=[]):
        return requests.patch(
            f"{self.base_url}/guilds/{guild_id}/roles",
            headers=self.auth_headers,
            data=json.dumps(positions)
        )

    @rate_limit()
    def modify_guild_role(self, guild_id, role_id, name, permissions=0, color=0, hoist=False, mentionable=False):
        role_data = {
            "name": name,
            "permissions": permissions,
            "color": color,
            "hoist": hoist,
            "mentionable": mentionable
        }

        return requests.patch(
            f"{self.base_url}/guilds/{guild_id}/roles/{role_id}",
            headers=self.auth_headers,
            data=json.dumps(role_data)
        )

    @rate_limit()
    def delete_guild_role(self, guild_id, role_id):
        return requests.delete(
            f"{self.base_url}/guilds/{guild_id}/roles/{role_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_guild_prune_count(self, guild_id, days=1):
        return requests.get(
            f"{self.base_url}/guilds/{guild_id}/prune",
            headers=self.auth_headers,
            data=json.dumps({"days": days})
        )

    @rate_limit()
    def begin_guild_prune(self, guild_id, days=1, compute_prune_count=False):
        return requests.post(
            f"{self.base_url}/guilds/{guild_id}/prune",
            headers=self.auth_headers,
            data=json.dumps({"days": days, "compute_prune_count": compute_prune_count})
        )

    @rate_limit()
    def get_guild_voice_regions(self, guild_id):
        return requests.get(
            f"{self.base_url}/guilds/{guild_id}/regions",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_guild_invites(self, guild_id):
        return requests.get(
            f"{self.base_url}/guilds/{guild_id}/invites",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_guild_integrations(self, guild_id):
        return requests.get(
            f"{self.base_url}/guilds/{guild_id}/integrations",
            headers=self.auth_headers
        )

    @rate_limit()
    def create_guild_integration(self, guild_id, **kwargs):
        return requests.post(
            f"{self.base_url}/guilds/{guild_id}/integrations",
            headers=self.auth_headers,
            data=json.dumps(kwargs)
        )

    @rate_limit()
    def modify_guild_integrations(self, guild_id, integration_id, **kwargs):
        return requests.post(
            f"{self.base_url}/guilds/{guild_id}/integrations/{integration_id}",
            headers=self.auth_headers,
            data=json.dumps(kwargs)
        )

    @rate_limit()
    def delete_guild_integration(self, guild_id, integration_id):
        return requests.delete(
            f"{self.base_url}/guilds/{guild_id}/integrations/{integration_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def sync_guild_integration(self, guild_id, integration_id):
        return requests.post(
            f"{self.base_url}/guilds/{guild_id}/integrations/{integration_id}/sync",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_guild_embed(self, guild_id):
        return requests.get(
            f"{self.base_url}/guilds/{guild_id}/embed",
            headers=self.auth_headers
        )

    @rate_limit()
    def modify_guild_embed(self, guild_id, **kwargs):
        return requests.patch(
            f"{self.base_url}/guilds/{guild_id}/embed",
            headers=self.auth_headers,
            data=json.dumps(kwargs)
        )

    @rate_limit()
    def list_guild_emojis(self, guild_id):
        return requests.get(
            f"{self.base_url}/guilds/{guild_id}/emojis",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_guild_emoji(self, guild_id, emoji_id):
        return requests.get(
            f"{self.base_url}/guilds/{guild_id}/emojis/{emoji_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def create_guild_emoji(self, guild_id, name, image_data, roles=None):
        roles = [] if roles is None else roles

        emoji_data = {
            "name": name,
            "image": image_data,
            "roles": roles
        }

        return requests.post(
            f"{self.base_url}/guilds/{guild_id}/emojis",
            headers=self.auth_headers,
            data=json.dumps(emoji_data)
        )

    @rate_limit()
    def modify_guild_emoji(self, guild_id, emoji_id, emoji_data):
        return requests.patch(
            f"{self.base_url}/guilds/{guild_id}/emojis/{emoji_id}",
            headers=self.auth_headers,
            data=emoji_data
        )

    @rate_limit()
    def delete_guild_emoji(self, guild_id, emoji_id):
        return requests.delete(
            f"{self.base_url}/guilds/{guild_id}/emojis/{emoji_id}",
            headers=self.auth_headers
        )

    # Webhooks
    @rate_limit()
    def create_webhook(self, channel_id, name=None, avatar=None):
        return requests.post(
            f"{self.base_url}/channels/{channel_id}/webhooks",
            headers=self.auth_headers,
            data=json.dumps({"name": name, "avatar": avatar})
        )

    @rate_limit()
    def get_channel_webhooks(self, channel_id):
        return requests.get(
            f"{self.base_url}/channels/{channel_id}/webhooks",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_guild_webhooks(self, guild_id):
        return requests.get(
            f"{self.base_url}/guilds/{guild_id}/webhooks",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_webhook(self, webhook_id):
        return requests.get(
            f"{self.base_url}/webhooks/{webhook_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def get_webhook_with_token(self, webhook_id, webhook_token):
        return requests.get(
            f"{self.base_url}/webhooks/{webhook_id}/{webhook_token}",
            headers=self.auth_headers
        )

    @rate_limit()
    def modify_webhook(self, webhook_id, name=None, avatar=None, channel_id=None):
        return requests.patch(
            f"{self.base_url}/webhooks/{webhook_id}",
            headers=self.auth_headers,
            data=json.dumps({"name": name, "avatar": avatar, "channel_id": channel_id})
        )

    @rate_limit()
    def modify_webhook_with_token(self, webhook_id, webhook_token, name=None, avatar=None):
        return requests.patch(
            f"{self.base_url}/webhooks/{webhook_id}/{webhook_token}",
            headers=self.auth_headers,
            data=json.dumps({"name": name, "avatar": avatar})
        )

    @rate_limit()
    def delete_webhook(self, webhook_id):
        return requests.delete(
            f"{self.base_url}/webhooks/{webhook_id}",
            headers=self.auth_headers
        )

    @rate_limit()
    def delete_webhook_with_token(self, webhook_id, webhook_token):
        return requests.delete(
            f"{self.base_url}/webhooks/{webhook_id}/webhook_token",
            headers=self.auth_headers
        )
