"""
    Class Name : Server

    Description:
        Storage unit for server data

    Contributors:
        - Patrick Hennessy

    License:
        CL4M-B0T is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

class Server():
    def __init__(self, id, name, channels={}):
        self.id = id
        self.name = name

        self.channels = channels

    def getChannel(self, channelID):
        if(channelID in self.channels):
            return self.channels[channelID]
        else:
            return None

    def addChannel(self, channel):
        if(channel.getID() not in self.channels):
            self.channels[channel.id] = channel

    def removeChannel(self, channel):
        if(channel.getID() in self.channels):
            del self.channels[channel.id]

    def getName(self):
        return self.name

    def getID(self):
        return self.id

    def updateChannels(self):
        pass
