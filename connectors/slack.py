"""
    Class Name : Slack Connector

    Description:
        Low-level communication interface between the bot core and the chat server
        This connector is intended for Slack.com
        It MUST subclass the abstract Connector class for consistancy and interoperability

    Contributors:
        - Patrick Hennessy

    License:
        CL4M-B0T is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Connector import Connector
from core.User import User
from core.Message import Message
from core.Channel import Channel

from urllib import urlencode
from urllib2 import urlopen
import json
import websocket
import threading
import time
from ssl import *

class SlackConnection(Connector):

    def __init__(self, **kwargs):
        self.api = SlackAPI()
        self.token = kwargs["token"]

        self.socket = None
        self.socketLock = threading.Lock()

    def connect(self):
        if not self.token:
            raise Exception("No token was provided. Add the auth token to the bot config file")

        # Initialize Slack websocket by polling the rtm.start() API method with authentication token
        reply = self.api.rtm.start(self.token)

        # Slack will send back an "ok": True message from the API call
        #   https://api.slack.com/methods/rtm.start
        if(reply["ok"]):
            self.socketURL = reply["url"]

            try:
                self.socket = websocket.create_connection(self.socketURL)
                self.socket.sock.setblocking(0)
            except:
                raise Exception("Could not establish a websocket to " + self.socketURL) # Could not establish a connection

            self.connected = True

        else:
            raise Exception("Authentication to Slack failed.")

    def disconnect(self):
        if(self.connected):
            self.connected = False
            self.socket.close()

    def ping(self):
        # https://api.slack.com/rtm
        return self.socket.send(json.dumps({"type":"ping"}))

    def send(self, message, channels):
        with self.socketLock:
            if(channels is not list and isinstance(channels, Channel)):
                channels = [channels]

            for channel in channels:
                self.socket.send(json.dumps({"type": "message", "channel": channel.id, "text": message}))

    def whisper(self, userID, message):
        pass

    def recieve(self):
        try:
            with self.socketLock:
                messages = self.socket.recv()

            if(messages):
                message = json.loads(messages.rstrip())

                if("type" in message.keys() and message["type"] == "message"):

                    return Message(
                        message["user"],
                        message["channel"],
                        message["ts"],
                        message["text"]
                    )
            else:
                return None

        # Catch exception where socket has not been fully read
        except SSLError:
            pass

    def getUsers(self):
        reply = self.api.users.list(self.token)

        if(reply["ok"]):
            return [self._parseUserData(user) for user in reply["members"]]

    def getUser(self, userID):
        reply = self.api.users.info(self.token, userID)

        if(reply["ok"]):
            return self._parseUserData(reply["user"])

    def _parseUserData(self, userData):
        user = User(
            userData["id"],
            userData["name"],
            realName=userData["profile"].get("real_name"),
            email=userData["profile"].get("email"),
            isAdmin=userData.get("is_admin")
        )

        return user

    def getChannels(self):
        reply = self.api.channels.list(self.token)

        if(reply["ok"]):
            return [self._parseChannelData(channel) for channel in reply["channels"]]

    def getChannel(self, channelID):
        reply = self.api.channels.info(self.token, channelID)

        if(reply["ok"]):
            return self._parseChannelData(reply["channel"])

    def _parseChannelData(self, channelData):
        channel = Channel(
            channelData["id"],
            channelData["name"],
            channelData.get("created"),
            creator=channelData.get("creator"),
            archived=channelData.get("is_archived")
        )

        return channel

"""
    API class specific to the Slack Bot API: https://api.slack.com/bot-users
"""
class SlackAPI():
    def __init__(self):
        self.api = api()
        self.auth = auth()
        self.channels = channels()
        self.chat = chat()
        self.emoji = emoji()
        self.groups = groups()
        self.im = im()
        self.rtm = rtm()
        self.users = users()

# Super class for all API calls
class _api():
    def __init__(self):
        pass

    def request(self, token, request="?", postData={}, domain="slack.com"):
        postData["token"] = token
        postData = urlencode(postData)

        url = 'https://{}/api/{}'.format(domain, request)

        response = urlopen(url, postData.encode('utf-8'))

        if(response.code != 200):
            raise Exception
        else:
            returnData = json.loads(response.read().decode('utf-8'))

            if not returnData["ok"]:
                error = returnData["error"]

                if(error == "invalid_auth"):
                    raise SlackAPI_InvalidAuth()
                elif(error == "not_authed"):
                    raise SlackAPI_NotAuthed()
                elif(error == "account_inactive"):
                    raise SlackAPI_AccountInactive()
                else:
                    raise SlackAPI_Exception("Unknown error code: " + error)

            else:
                return returnData

class api(_api):
    def __init__(self):
        pass

    def test(self, token, error="", foo=""):
        return self.request(token, "api.test", postData={"error": error, "foo": foo})

class auth(_api):
    def __init__(self):
        pass

    def test(self, token):
        return self.request(token, "auth.test")

class channels(_api):
    def __init__(self):
        pass

    def history(self, token, channelID):
        return self.request(token, "channels.history", postData={"channel":channelID})

    def info(self, token, channelID):
        return self.request(token, "channels.info", postData={"channel":channelID})

    def list(self, token, excludeArchived=0):
        return self.request(token, "channels.list", postData={"exclude_archived": excludeArchived})

    def mark(self, token, channelID, timestamp):
        return self.request(token, "channels.mark", postData={"channel": channelID, "ts": timestamp})

    def setPurpose(self, token, channelID, purpose):
        return self.request(token, "channels.list", postData={"channel": channelID, "purpose": purpose})

    def setTopic(self, token, channelID, topic):
        return self.request(token, "channels.list", postData={"channel": channelID, "topic": topic})

class chat(_api):
    def __init__(self):
        pass

    def delete(self, token, timestamp, channelID):
        return self.request(token, "chat.delete", postData={"ts": timestamp, "channel":channelID})

    def postMessage(self, token, channelID, message):
        return self.request(token, "chat.postMessage", postData={"channel":channelID, "text": message})

    def update(self, token, channelID, message, timestamp):
        return self.request(token, "chat.update", postData={"channel":channelID, "text": message, "ts":timestamp})

class emoji(_api):
    def __init__(self):
        pass

    def list(self, token):
        return self.request(token, "emoji.list")

class groups(_api):
    def __init__(self):
        pass

    def close(self, token, groupID):
        return self.request(token, "groups.close", postData={"channel":groupID})

    def history(self, token, groupID):
        return self.request(token, "groups.history", postData={"channel":groupID})

    def info(self, token, groupID):
        return self.request(token, "groups.info", postData={"channel":groupID})

    def list(self, token, excludeArchived=0):
        return self.request(token, "groups.close", postData={"exclude_archived": excludeArchived})

    def mark(self, token, groupID, timestamp):
        return self.request(token, "groups.close", postData={"channel":groupID, "ts":timestamp})

    def open(self, token, groupID):
        return self.request(token, "groups.open", postData={"channel":groupID})

    def setPurpose(self, token, groupID, purpose):
        return self.request(token, "groups.setPurpose", postData={"channel":groupID, "purpose": purpose})

    def setTopic(self, token, groupID, topic):
        return self.request(token, "groups.setPurpose", postData={"channel":groupID, "topic": topic})

class im(_api):
    def __init__(self):
        pass

    def close(self, token, channelID):
        return self.request(token, "im.close", postData={"channel":channelID})

    def history(self, token):
        pass

    def list(self, token):
        return self.request(token, "im.list")

    def mark(self, token, channelID, timestamp):
        return self.request(token, "im.mark", postData={"channel":channelID, "ts":timestamp})

    def open(self, token, userID):
        return self.request(token, "im.open", postData={"channel":channelID, "user": userID})

class rtm(_api):
    def __init__(self):
        pass

    def start(self, token):
        return self.request(token, "rtm.start")

class users(_api):
    def __init__(self):
        pass

    def getPresence(self, userID):
        return self.request(token, "users.getPresence", postData={"user":userID})

    def info(self, token, userID):
        return self.request(token, "users.info", postData={"user":userID})

    def list(self, token):
        return self.request(token, "users.list")

    def setPresence(self, token, presence):
        return self.request(token, "users.getPresence", postData={"presence": presence})


class SlackAPI_Exception(Exception):
    def __init__(self, value=""):
        self.value = value

    def __str__(self):
        return repr(self.value)

class SlackAPI_InvalidAuth(SlackAPI_Exception):
    def __init__(self):
        self.value = "Invalid authentication token."

class SlackAPI_NotAuthed(SlackAPI_Exception):
    def __init__(self):
        self.value = "No authentication token provided."

class SlackAPI_AccountInactive(SlackAPI_Exception):
    def __init__(self):
        self.value = "Authentication token is for a deleted user or team."

class SlackAPI_ChannelNotFound(SlackAPI_Exception):
    def __init__(self):
        self.value = "Value passed for channelID was invalid."

class SlackAPI_NotInChannel(SlackAPI_Exception):
    def __init__(self):
        self.value = "Caller is not a member of the channel."

class SlackAPI_UserRestricted(SlackAPI_Exception):
    def __init__(self):
        self.value = "This method cannot be called by a restricted user or single channel guest."

class SlackAPI_PurposeTooLong(SlackAPI_Exception):
    def __init__(self):
        self.value = "Value passed for purpose was longer than 250 characters."

class SlackAPI_TopicTooLong(SlackAPI_Exception):
     def __init__(self):
        self.value = "Value passed for topic was longer than 250 characters."


class SlackAPI_ChannelArchived(SlackAPI_Exception):
    def __init__(self):
        self.value = "Channel has been archived."

class SlackAPI_MessageNotFound(SlackAPI_Exception):
    def __init__(self):
        self.value = "No message exists with the requested timestamp."

class SlackAPI_CannotDeleteMessage(SlackAPI_Exception):
    def __init__(self):
        self.value = "Authenticated user does not have permission to delete this message."

class SlackAPI_MessageTooLong(SlackAPI_Exception):
    def __init__(self):
        self.value = "Message text is too long."

class SlackAPI_NoTextProvided(SlackAPI_Exception):
    def __init__(self):
        self.value = "Message must contain text."

class SlackAPI_UserNotInChannel(SlackAPI_Exception):
    def __init__(self):
        self.value = "Cannot post user messages to a channel they are not in."

class SlackAPI_RateLimited(SlackAPI_Exception):
    def __init__(self):
        self.value = "Application has posted too many messages too quickly."

class SlackAPI_EditWindowClosed(SlackAPI_Exception):
    def __init__(self):
        self.value = "The message cannot be edited due to the team message edit settings"

class SlackAPI_DoesNotOwnChannel(SlackAPI_Exception):
    def __init__(self):
        self.value = "Calling user does not own this DM channel."

class SlackAPI_UserNotVisible(SlackAPI_Exception):
    def __init__(self):
        self.value = "The calling user is restricted from seeing the requested user."

class SlackAPI_MigrationInProgress(SlackAPI_Exception):
    def __init__(self):
        self.value = "Team is being migrated between servers."

class SlackAPI_UserNotFound(SlackAPI_Exception):
    def __init__(self):
        self.value = "Value passed for user was invalid."

class SlackAPI_InvalidPressence(SlackAPI_Exception):
    def __init__(self):
        self.value = "Value passed for presence was invalid. Must be 'auto' or 'away'"
