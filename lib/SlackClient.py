import websocket
import json
import time
import threading

from ssl import *
from lib.SlackAPI import SlackAPI

class SlackConnection():

    def __init__(self, token):

        self.slackAPI   = SlackAPI()    # Python implemented interface for hitting Slack API
        self.token      = token

        self.socket     = None
        self.socketURL  = None

        self.loginData  = None
        self.channels   = []

        self.messageThread = None
        self.messageBuffer = []

        self.connected  = False

    def ping(self):
        return self.socket.send(json.dumps({"type":"ping"}))

    def connect(self):
        # Initialize Slack websocket by polling the [rtm.start] API method with authentication token
        reply = self.slackAPI.rtm.start(self.token)

        if(reply["ok"]):
            self.connected = True
            self.parseLoginData(reply)

            try:
                self.socket = websocket.create_connection(self.socketURL)
                self.socket.sock.setblocking(0)
            except:
                raise SlackConnectionError # Could not establish a connection

            self.messageThread = threading.Thread(target=self.recv)
            self.messageThread.start()
        else:
            pass # Unable to login

    def disconnect(self):
        self.socket.close()
        self.connected = False

    def emit(self, channel, message):
        channelID = self.getChannelID(channel)

        if not channelID:
            self.log.error("Channel \"" + channel + "\" does not exist")
        else:
            self.socket.send(json.dumps({"type": "message", "channel": channelID, "text": message}))

    def recv(self):
        while True:
            try:
                data = self.socket.recv()

                data = data.rstrip()
                data = json.loads(data)

                self.messageBuffer.append(data)
            except SSLError:
                pass
            except websocket._exceptions.WebSocketConnectionClosedException:
                print "Disconnected while recv..."

    def getMessage(self):
        if(len(self.messageBuffer) > 0 ):
            returnBuffer = self.messageBuffer
            self.messageBuffer = []

            return returnBuffer
        else:
            return None

    def parseLoginData(self, loginData):

        self.loginData  = loginData
        self.socketURL  = self.loginData["url"]

        self.parseChannelData(loginData["channels"])
        self.parseChannelData(loginData["groups"])
        self.parseChannelData(loginData["ims"])

    def parseChannelData(self, channels):
         for channel in channels:
            if "name" not in channel.keys():
                channel["name"] = channel["id"]

            if "members" not in channel.keys():
                channel["members"] = []

            self.channels.append(Channel(channel["name"], channel["id"], channel["members"]))

    def getChannelID(self, searchTerm):
        for channel in self.channels:
            if(searchTerm.lower() == channel.name.lower() or searchTerm == channel.id):
                return channel.id

        return False

    def getBotData(self):
        return {"domain": self.loginData["team"]["domain"], "username": self.loginData["self"]["name"], "id": self.loginData["self"]["id"]}

    def getUserData(self, id):
        return self.slackAPI.users.info(self.token, id)


class SlackConnectionError(Exception):
    pass

class SlackLoginError(Exception):
    pass



class Channel():
    def __init__(self, name, id, members=[]):
        self.name = name
        self.id = id
        self.members = members

    def send_message(self, message):
        message_json = {"type": "message", "channel": self.id, "text": message}
        #self.server.send_to_websocket(message_json)
