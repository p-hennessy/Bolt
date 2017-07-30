"""
    Class Name : Webhook

    Description:


    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation



            @webhook("/notify/git", type="POST")
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

class WebhookManager():
    def __init__(self, core, port):
        self.core = core
        self.server = HTTPServer(port)
        self.listening = False

    def register(self, method, uri, callback):
        pass

    def unregister(self):
        pass


class HTTPServer():
    def __init__(self, port):
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind( ('127.0.0.1', port) )
        self.socket.listen(5)
        self.socket.setblocking(0)

        self.thread = None

    def start(self):
        self.listening = True
        self.thread = threading.Thread(target=self.listen)
        self.thread.start()

    def stop(self):
        self.listening = False
        self.thread.join()

    def listen(self):
        while self.listening:
            time.sleep(0.5)

            try:
                connection, address = self.socket.accept()
            except socket.error as e:
                # Resource timeout
                if(e.errno == 11):
                    continue

            requestData = connection.recv(1024)
            request = self.parseRequest(requestData, connection)

            print request

    def parseRequest(self, requestData, connection):
        request = {}
        requestData = requestData.splitlines()

        for index, line in enumerate(requestData):
            if(index == 0):
                try:
                    method, uri, version = line.split(" ")

                    request["method"] = method
                    request["uri"] = uri
                    request["version"] = version

                except:
                    # When they send a malformed header
                    connection.send("HTTP/1.1 400 Bad Request")
                    connection.close()

                # Check HTTP Method
                if method not in ["POST", "GET", "HEAD", "OPTIONS", "PUT", "DELETE", "TRACE", "PATCH"]:
                    connection.send("HTTP/1.1 405 Method Not Allowed")
                    connection.close()

                # Check HTTP version
                if version not in ["HTTP/1.1", "HTTP/1.0"]:
                    connection.send("HTTP/1.1 505 HTTP Version Not Supported")
                    connection.close()

            elif(line.startswith("Content-Type")):
                request["contentType"] = line.split(" ")[1]

            elif(line.startswith("Content-Length")):
                request["contentLength"] = line.split(" ")[1]

            else:
                if(line != ""):
                    request["payload"] = line

        return request
