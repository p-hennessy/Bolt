"""
    Class Name : Webhook

    Description:


    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation

    @webhook("/notify/git", method="POST")
    def example(self, request):
            request
                sender
                type
                body
                headers

"""

import socket
import threading
import sys
import time
import json


def webhook(route, methods):
    def decorate(callback):
        def wrapper(self, *args, **kwargs):
            return callback(self, *args, **kwargs)

        return wrapper
    return decorate



#from bottle import Bottle, run, Route, request, response

class WebhookManager():
    def __init__(self):
        pass

    def register(self):
        pass

    def unregister(self):
        pass

    def run(self):
        pass

#
# app = Bottle()
#
#
# def index():
#     app.route('/world', callback=world)
#     print(request)
#
#     return 'Hello!'
#
#
# def world():
#     return 'World!'
#
# app.route("/", callback=index)
# run(app)
