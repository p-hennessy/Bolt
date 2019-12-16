from gevent.pywsgi import WSGIServer
import logging
import ujson as json
import falcon


class WebhookServer():
    def __init__(self, bot):
        self.bot = bot
        self.routes = {}
        self.app = falcon.API()
        self.app.add_sink(self.handle, '/')

        self.logger = logging.getLogger(__name__)
        self.server = WSGIServer(('', 8080), self.app, log=self.logger)

    def start(self):
        self.logger.debug('Spawning WebhookServer greenlet')
        self.server.serve_forever()

    def handle(self, request, response):
        route = request.path
        method = request.method

        for plugin in self.bot.plugins:
            if not plugin.enabled:
                continue

            for webhook in plugin.webhooks:
                if not route == webhook.route:
                    continue
                else:
                    if method not in webhook.methods:
                        response.status = falcon.HTTP_405
                        return response
                    else:
                        try:
                            request_data = json.loads(request.stream.read())
                            request_headers = request.headers
                            ret = webhook.callback(request_data, request_headers)

                            if isinstance(ret, str):
                                response.body = ret
                            elif isinstance(ret, dict):
                                response.body = json.dumps(ret)

                            response.status = falcon.HTTP_200
                            return response

                        except Exception as e:
                            self.logger.warning(f"Recieved exception processing web request: {e}")
                            response.status = falcon.HTTP_500
                            return response
        else:
            response.status = falcon.HTTP_404
            return response


class Webhook():
    def __init__(self, route, callback, methods=None):
        methods = ["GET"] if methods is None else methods

        if not route.startswith("/"):
            route = "/" + str(route)

        self.route = route
        self.callback = callback
        self.methods = methods
