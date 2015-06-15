from urllib import urlencode 
from urllib2 import urlopen

import json
 
class SlackAPI():
    def __init__(self):
        self.rtm = rtm()
        self.channels = channels()
        
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

class channels(API):
    def __init__(self):
        pass
    
    
class rtm(API):
    def __init__(self):
        pass

    def start(self, token):
        return self.request(token, "rtm.start")

