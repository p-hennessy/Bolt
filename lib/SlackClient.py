import websocket
import json
import time

from ssl import *
from lib.SlackAPI import SlackAPI
from lib.Logger import *

class SlackConnection():
    def __init__(self, token):
        
        self.slackAPI   = SlackAPI()
        self.log        = Logger()
        self.token      = token
        
        self.socket     = None
        self.socketURL  = None

        self.loginData  = None
        self.users      = []
        self.channels   = []
        
        self.connected  = False
        self.pingcounter = 0

        self.connect()

    
    def getChannelID(self, searchTerm):
        for channel in self.channels:
            if(searchTerm.lower() == channel.name.lower() or searchTerm == channel.id):
                return channel.id
        
        return False
    
    def getBotData(self):
        return {"domain": self.loginData["team"]["domain"], "username": self.loginData["self"]["name"], "id": self.loginData["self"]["id"]}

    def getUserData(self, id):
        return self.slackAPI.users.info(self.token, id)
    
    def connect(self):
        reply = self.slackAPI.rtm.start(self.token)
                
        if(reply["ok"]):
            self.parseLoginData(reply)
            
            try:
                self.socket = websocket.create_connection(self.socketURL)
                self.socket.sock.setblocking(0) 
            except:
                raise SlackConnectionError
                
        else:
            raise SlackLoginError

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

    def disconnect(self):
        self.socket.close()
    
    def emit(self, channel, message):
        channelID = self.getChannelID(channel)
        
        if not channelID:
            self.log.error("Channel \"" + channel + "\" does not exist")
        else:
            self.socket.send(json.dumps({"type": "message", "channel": channelID, "text": message}))
        
    def recv(self):
        data = ""
        while True:
            try:
                data += self.socket.recv()
            except SSLError:
                return None
            
            data = data.rstrip()
            data = json.loads(data)
            
            return data

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
        
        
