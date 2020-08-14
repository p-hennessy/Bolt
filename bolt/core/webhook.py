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
                    continue
                else:
                    try:
                        if request.method in ["POST", "PATCH"]:
                            request_data = json.loads(request.stream.read())
                        elif request.method == "GET":
                            request_data = request.params
                        else:
                            request_data = {}
                            
                        ret = webhook.callback(request_data, request.headers)

                        if isinstance(ret, str):
                            response.body = ret
                        elif isinstance(ret, dict):
                            response.body = json.dumps(ret)

                        response.status = falcon.HTTP_200
                        break

                    except Exception as e:
                        self.logger.warning(f'Caught exception handling webhook: {e}')
                        response.status = falcon.HTTP_500
                        break
        else:
            response.status = falcon.HTTP_404

        dash = "-"
        line = (
            f"{request.method.upper()} "
            f"{request.path} "
            f"{request.content_length or dash} "
            f"{request.host} "
            f"{request.user_agent or dash} "
            f"{time.time() - start_time:.2f}ms "
            f"{response.status}"
        )
        self.logger.info(line)
        return response


class Webhook():
    def __init__(self, route, callback, methods=None):
        methods = ["GET"] if methods is None else methods

        if not route.startswith("/"):
            route = "/" + str(route)

        self.route = route
        self.callback = callback
        self.methods = methods
