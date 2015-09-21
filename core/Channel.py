"""
    Class Name : Channel

    Description:
        Provides staging area for channel data

    Contributors:
        - Patrick Hennessy

    License:
        PhilBot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

class Channel():
    def __init__(self, id, name, created=0, creator=None, archived=False):
        self.id = id
        self.name = name
        self.created = created
        self.creator = creator
        self.archived = archived

class ChannelManager():

    def __init__(self, core, channels=[]):
        self.core = core
        self.channels = channels

    def addChannel(self, channel):
        self.channels.append(channel)

    def removeChannel(self, cid):
        for channel in self.channels:
            if(channel.id == uid):
                self.channels.remove(channel)

    def updateChannelList(self):
        self.channels = self.core.connection.getChannels()

    def getChannelList(self):
        self.updateUserList()

        return self.channels

    def getChannel(self, cid):
        for channel in self.channels:
            if(channel.id == cid):
                return channel

        newChannel = self.core.connection.getChannel(cid)
        self.addChannel(newChannel)

        return newChannel
