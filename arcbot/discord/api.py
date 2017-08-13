"""
    This module provides a class that implements the full spec of the Discord API
    https://discordapp.com/developers/docs/

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it under the terms of the GNU
        General Public License v3; as published by the Free Software Foundation
"""
import gevent
import requests

class API():
    def __init__(self, token):
        self.auth_headers = {
            "authorization": "Bot " + token,
            "Content-Type": 'application/json'
        }
        self.base_url = "https://discordapp.com/api"

    # Gateway
    def get_gateway(self):
        """
            URL: https://discordapp.com/developers/docs/topics/gateway#get-gateway
            Description:
                Returns an object with a single valid WSS URL, which the client can use as a basis
                for Connecting. Clients should cache this value and only call this endpoint to
                retrieve a new URL if they are unable to properly establish a connection using the
                cached version of the URL.
        """
        uri = f"{self.base_url}/gateway"
        headers = self.auth_headers

        response = requests.get(uri, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_gateway_bot(self):
        """
            URL: https://discordapp.com/developers/docs/topics/gateway#get-gateway-bot
            Description:
                Returns an object with the same information as Get Gateway, plus a shards key,
                containing the recommended number of shards to connect with (as an integer). Bots
                that want to dynamically/automatically spawn shard processes should use this
                endpoint to determine the number of processes to run. This route should be called
                once when starting up numerous shards, with the response being cached and passed to
                all sub-shards/processes. Unlike the Get Gateway, this route should not be cached
                for extended periods of time as the value is not guaranteed to be the same per-call,
                and changes as the bot joins/leaves guilds.
        """
        uri = f"{self.base_url}/gateway/bot"
        headers = self.auth_headers

        response = requests.get(uri, headers=headers)
        response.raise_for_status()
        return response.json()

    # Channel : https://discordapp.com/developers/docs/resources/channel
    def get_channel(self, channel_id):
        """
            URL: https://discordapp.com/developers/docs/resources/channel#get-channel
            Description:
                Get a channel by ID. Returns a guild channel or dm channel object.
        """
        uri = f"{self.base_url}/channels/{channel_id}"
        headers = self.auth_headers

        response = requests.get(uri, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_channel_messages(self, channel_id):
        """
            URL: https://discordapp.com/developers/docs/resources/channel#get-channel-messages
            Description:
                Returns the messages for a channel. If operating on a guild channel, this endpoint
                requires the 'READ_MESSAGES' permission to be present on the current user. Returns
                an array of message objects on success.
        """
        uri = f"{self.base_url}/channels/{channel_id}/messages"
        headers = self.auth_headers

        response = requests.get(uri, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_channel_message(self, channel_id, message_id):
        """
            URL: https://discordapp.com/developers/docs/resources/channel#get-channel-message
            Description:
                Returns a specific message in the channel. If operating on a guild channel, this
                endpoints requires the 'READ_MESSAGE_HISTORY' permission to be present on the
                current user. Returns a message object on success.
        """
        uri = f"{self.base_url}/channels/{channel_id}/messages/{message_id}"
        headers = self.auth_headers

        response = requests.get(uri, headers=headers)
        response.raise_for_status()
        return response.json()

    def modify_channel(self, channel_id, **kwargs):
        """
            URL: https://discordapp.com/developers/docs/resources/channel#modify-channel
            Description:
                Update a channels settings. Requires the 'MANAGE_CHANNELS' permission for the guild.
                Returns a guild channel on success, and a 400 BAD REQUEST on invalid parameters.
                Fires a Channel Update Gateway event. For the PATCH method, all the JSON Params are
                optional.
        """
        uri = f"{self.base_url}/channels/{channel_id}"
        headers = self.auth_headers

        response = requests.patch(uri, data=json.dumps(kwargs), headers=headers)
        response.raise_for_status()
        return response.json()

    def delete_channel(self, channel_id):
        """
            URL: https://discordapp.com/developers/docs/resources/channel#modify-channel
            Description:
                Delete a guild channel, or close a private message. Requires the 'MANAGE_CHANNELS'
                permission for the guild. Returns a guild channel or dm channel object on success.
                Fires a Channel Delete Gateway event.
        """
        uri = f"{self.base_url}/channels/{channel_id}"
        headers = self.auth_headers

        response = requests.delete(uri, headers=headers)
        response.raise_for_status()
        return response.json()

    def delete_own_reaction(self, channel_id):
        permissions = ['MANAGE_CHANNELS', 'READ_MESSAGES']

        with self.permissions(permissions):
            uri = f"{self.base_url}/channels/{channel_id}/messages"
            headers = self.auth_headers

            if isinstance(message_data, dict):
                message_data = json.dumps(message_data)

            response = requests.post(uri, data=message_data, files=files, headers=headers)
            response.raise_for_status()


    def create_message(self, channel_id, message_data, files=None):
        """
            URL: https://discordapp.com/developers/docs/resources/channel#create-message
            Description:
                Post a message to a guild text or DM channel. If operating on a guild channel,
                this endpoint requires the 'SEND_MESSAGES' permission to be present on the current
                user. Returns a message object. Fires a Message Create Gateway event. See message
                formatting for more information on how to properly format messages.
        """
        uri = f"{self.base_url}/channels/{channel_id}/messages"
        headers = self.auth_headers

        if isinstance(message_data, dict):
            message_data = json.dumps(message_data)

        response = requests.post(uri, data=message_data, files=files, headers=headers)
        response.raise_for_status()

    def create_reaction(self, channel_id, message_id, emoji):
        """
            URL: https://discordapp.com/developers/docs/resources/channel#create-reaction
            Description:
                Create a reaction for the message. This endpoint requires the 'READ_MESSAGE_HISTORY'
                permission to be present on the current user. Additionally, if nobody else has
                reacted to the message using this emoji, this endpoint requires the 'ADD_REACTIONS'
                permission to be present on the current user. Returns a 204 empty response on
                success.
        """
        uri = f"{self.base_url}/channels/{channel_id}/messages/{messsage_id}/reactions/{emoji}/@me"
        headers = self.auth_headers

        response = requests.put(uri, headers=headers)
        response.raise_for_status()
        return response.json()


    # User : https://discordapp.com/developers/docs/resources/user

    def get_current_user(self):
        uri = f"{self.base_url}/users/@me"
        headers = self.auth_headers

        response = requests.get(uri, headers=headers)
        response.raise_for_status()

        return response.json()

    def get_user(self, user_id):
        uri = f"{self.base_url}/users/{user_id}"
        headers = self.auth_headers

        response = requests.get(uri, headers=headers)
        response.raise_for_status()

        return response.json()

    def modify_current_user(self, username, avatar_data=None):
        uri = f"{self.base_url}/users/@me"
        headers = self.auth_headers

        data = {
            "username": username,
            "avatar": avatar_data
        }

        response = requests.post(uri, headers=headers)
        response.raise_for_status()

        return response.json()

    def get_current_user_guilds(self):
        uri = f"{self.base_url}/users/@me/guilds"
        headers = self.auth_headers

        response = requests.get(uri, headers=headers)
        response.raise_for_status()

        return response.json()

    def leave_guild(self, guild_id):
        uri = f"{self.base_url}/users/@me/guilds/{guild_id}"
        headers = self.auth_headers

        response = requests.delete(uri, headers=headers)
        response.raise_for_status()

    def get_user_dms(self):
        uri = f"{self.base_url}/users/@me/channels"
        headers = self.auth_headers

        response = requests.get(uri, headers=headers)
        response.raise_for_status()

        return response.json()

    def create_dm(self, user_id):
        """
            URL: https://discordapp.com/developers/docs/resources/user#create-dm
            Description:
                Create a new DM channel with a user. Returns a DM channel object.
        """
        uri = f"{self.base_url}/users/@me/channels"
        headers = self.auth_headers
        data={
            "recipient_id": f"{user_id}"
        }

        response = requests.post(uri, data=json.dumps(data), headers=headers)
        response.raise_for_status()

        return response.json()

    def get_user_connections(self):
        """
            URL: https://discordapp.com/developers/docs/resources/user#get-user-connections
            Description:
                Returns a list of connection objects. Requires the connections OAuth2 scope.
        """
        uri = f"{self.base_url}/users/@me/connections"
        headers = self.auth_headers

        response = requests.get(uri, headers=headers)
        response.raise_for_status()

        return response.json()

    def trigger_typing(self, channel_id):
        """
            URL: https://discordapp.com/developers/docs/resources/channel#trigger-typing-indicator
            Description:
                Post a typing indicator for the specified channel. Generally bots should not
                implement this route. However, if a bot is responding to a command and expects the
                computation to take a few seconds, this endpoint may be called to let the user know
                that the bot is processing their message. Returns a 204 empty response on success.
                Fires a Typing Start Gateway event.
        """
        uri = f"{self.base_url}/channels/{channel_id}/typing"
        headers = self.auth_headers

        response = requests.post(uri, headers=headers)
        response.raise_for_status()

    # Guild
    def get_guild_roles(self, guild_id):
        uri = f"{self.base_url}/guilds/{guild_id}/roles"
        headers = self.auth_headers

        response = requests.get(uri, headers=headers)
        response.raise_for_status()

        return response.json()

    def get_guild_member(self, guild_id, user_id):
        uri = f"{self.base_url}/guilds/{guild_id}/members/{user_id}"
        headers = self.auth_headers

        response = requests.get(uri, headers=headers)
        response.raise_for_status()

        return response.json()

    def create_guild_channel(self, guild_id, name, **kwargs):
        """
            URL: https://discordapp.com/developers/docs/resources/guild#create-guild-channel
            Description:
                Create a new channel object for the guild. Requires the 'MANAGE_CHANNELS' permission
                Returns the new channel object on success. Fires a Channel Create Gateway event.
        """
        uri = f"{self.base_url}/guilds/{guild_id}/channels"
        headers = self.auth_headers

        data = {
            "name": name
        }
        data.update(**kwargs)

        response = requests.post(uri, data=json.dumps(data), headers=headers)
        response.raise_for_status()

        return response.json()
