"""
    API class specific to the Slack Bot API: https://api.slack.com/bot-users
"""

from urllib import urlencode 
from urllib2 import urlopen

import json
 
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
        
class API():
    def __init__(self):
        pass
        
    def request(self, token, request="?", postData={}, domain="slack.com"):
        postData["token"] = token
        postData = urlencode(postData)

        url = 'https://{}/api/{}'.format(domain, request)

        returnData = urlopen(url, postData.encode('utf-8'))
        
        if(returnData.code != 200):
            raise Exception
        else:
            return json.loads(returnData.read().decode('utf-8'))

class api(API):
    def __init__(self):
        pass
    
    def test(self, token, error="", foo=""):
        return self.request(token, "api.test", postData={"error": error, "foo": foo})

class auth(API):
    def __init__(self):
        pass
    
    def test(self, token):
        return self.request(token, "auth.test")
        
class channels(API):
    def __init__(self):
        pass
    
    def history(self, token, channelID):
        return self.request(token, "channels.history", postData={"channel":channelID})
    
    def info(self, token, channelID):
        return self.request(token, "channels.info", postData={"channel":channelID})

    def list(self, token, channelID, excludeArchived=0):
        return self.request(token, "channels.list", postData={"exclude_archived": excludeArchived})

    def mark(self, token, channelID, timestamp):
        return self.request(token, "channels.mark", postData={"channel": channelID, "ts": timestamp})

    def setPurpose(self, token, channelID, purpose):
        return self.request(token, "channels.list", postData={"channel": channelID, "purpose": purpose})

    def setTopic(self, token, channelID, topic):
        return self.request(token, "channels.list", postData={"channel": channelID, "topic": topic})

class chat(API):
    def __init__(self):
        pass
    
    def delete(self, token, timestamp, channelID):
        return self.request(token, "chat.delete", postData={"ts": timestamp, "channel":channelID})

    def postMessage(self, token, channelID, message):
        return self.request(token, "chat.postMessage", postData={"channel":channelID, "text": message})
    
    def update(self, token, channelID, message, timestamp):
        return self.request(token, "chat.update", postData={"channel":channelID, "text": message, "ts":timestamp})
       
class emoji(API):
    def __init__(self):
        pass
    
    def list(self, token):
        return self.request(token, "emoji.list")

class groups(API):
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

class im(API):
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
        
class rtm(API):
    def __init__(self):
        pass

    def start(self, token):
        return self.request(token, "rtm.start")

class users(API):
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
