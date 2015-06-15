import websocket
import json
import time

from ssl import *
from lib.SlackAPI import SlackAPI

class SlackConnection():
    def __init__(self, token):
        
        self.slackAPI = SlackAPI()
        self.token = token
        
        self.socket = None
        self.socketURL = None
        
        self.botData = {}
        self.channels = []
        
        self.connect()
    
    def getChannelID(self, searchTerm):
        for channel in self.channels:
            if(searchTerm == channel["name"].lower() or searchTerm == channel["id"]):
                return channel["id"]
        
        return False
    
    def getUserData(self, user=None):
        if not user:
            return self.botData
        
        #TODO: handle getting user data for other users
        
        
    def connect(self):
        reply = self.slackAPI.rtm.start(self.token)
                
        if (reply.code != 200):
            raise SlackConnectionError
        else:
            replyJSON = json.loads(reply.read().decode('utf-8'))
            
            self.botData = replyJSON["self"]
        
            if(replyJSON["ok"]):
                
                self.channels = replyJSON["channels"]
                self.socketURL = replyJSON["url"]
    
                try:
                    self.socket = websocket.create_connection(self.socketURL)
                    self.socket.sock.setblocking(0)
                except:
                    raise SlackConnectionError
            else:
                raise SlackLoginError
            
    def disconnect(self):
        self.websocket.close()
            
    def emit(self, channel, message):
        channel = self.getChannelID(channel)
        
        if not channel:
            print "Channel does not exist"
        else:
            self.socket.send(json.dumps({"type": "message", "channel": channel, "text": message}))
        
    def recv(self):
        data = ""
        while True:
            try:
                data += self.socket.recv()
            except SSLError:
                continue
            
            data = data.rstrip()
            data = json.loads(data)
            
            if("type" in data.keys() and data["type"] == "message"):
                return data
            else:
                return

class SlackConnectionError(Exception):
    pass        
        
class SlackLoginError(Exception):
    pass        
        
    