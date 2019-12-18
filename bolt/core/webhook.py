from gevent.pywsgi import WSGIServer
import logging
import time
import ujson as json
import falcon


class WebhookServer():
    def __init__(self, bot):
        self.bot = bot
        self.routes = {}
        self.app = falcon.API()
        self.app.add_sink(self.handle, '/')

        self.logger = logging.getLogger(__name__)
        self.server = WSGIServer(('', 8080), self.app, log=None)

    def start(self):
        self.logger.debug('Spawning WebhookServer greenlet')
        self.server.serve_forever()

    def get_webhooks(self):
        for plugin in self.bot.plugins:
            if plugin.enabled is False:
                continue

            for webhook in plugin.webhooks:
                yield webhook

    def handle(self, request, response):
        start_time = time.time()

        for webhook in self.get_webhooks():
            if not request.path == webhook.route:
                continue
            else:
                if request.method not in webhook.methods:
                    response.status = falcon.HTTP_405
                    break
                else:
                    try:
                        request_data = json.loads(request.stream.read())
                        ret = webhook.callback(request_data, request.headers)

                        if isinstance(ret, str):
                            response.body = ret
                        elif isinstance(ret, dict):
                            response.body = json.dumps(ret)

                        response.status = falcon.HTTP_200
                        break

                    except Exception:
                        response.status = falcon.HTTP_500
                        break
        else:
            response.status = falcon.HTTP_404

        self.logger.info(f"""
            {request.method.upper()}
            '{request.path}'
            {request.content_length or "-"}
            {request.host}
            {request.user_agent or "-"}
            {float(time.time() - start_time):.2}ms
            '{response.status}'
        """)
        return response


class Webhook():
    def __init__(self, route, callback, methods=None):
        methods = ["GET"] if methods is None else methods

        if not route.startswith("/"):
            route = "/" + str(route)

        self.route = route
        self.callback = callback
        self.methods = methods
