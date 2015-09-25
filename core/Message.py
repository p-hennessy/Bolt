"""
    Class Name : MessageParser

    Description:
        Simple class to standardize message data

    Contributors:
        - Patrick Hennessy

    License:
        CL4M-B0T is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""
import time

class Message():
    class text():
        def __init__(self, sender, channel, text, timestamp=time.time(), server=None):
            self.sender = sender
            self.channel = channel
            self.server = server
            self.timestamp = timestamp
            self.text = text

    class pressence():
        def __init__(self, sender, status, timestamp=time.time()):
            self.sender = sender
            self.status = status
            self.timestamp = timestamp
