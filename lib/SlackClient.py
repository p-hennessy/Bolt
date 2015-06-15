import websocket
import json

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
        self.slackAPI.rtm.start()
        
        reply = self.slackAPI.rtmStart(self.token)
        
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
            
    def emit(self, channel, message):
        channel = self.getChannelID(channel)
        
        if not channel:
            print "Channel does not exist"
        else:
            self.socket.send(json.dumps({"type": "message", "channel": channel, "text": message}))
        
    def listen(self):
        data = ""
        while True:
            try:
                data += "{}\n".format(self.websocket.recv())
            except SSLWantReadError:
                return ''
            
            return data.rstrip()
        

class SlackConnectionError(Exception):
    pass        
        
class SlackLoginError(Exception):
    pass        
        
    