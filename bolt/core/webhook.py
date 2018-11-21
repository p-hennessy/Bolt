from gevent.pywsgi import WSGIServer
import logging
import ujson as json
import falcon

class WebhookServer():
    def __init__(self):
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

        if route not in self.routes.keys():
            response.status = falcon.HTTP_404
            return response

        route_data = self.routes[route]

        if method not in route_data['methods']:
            response.status = falcon.HTTP_405
            return response

        try:
            ret = route_data['callback'](request)

            if isinstance(ret, str):
                response.body = ret
            elif isinstance(ret, dict):
                response.body = json.dumps(ret)

            response.status = falcon.HTTP_200
            return response

        except Exception as e:
            self.logger.warning(f"Recieved exception processing web request: {e}")
            response.status = falcon.HTTP_500

    def add_route(self, route, callback, methods=['GET']):
        if not route.startswith("/"):
            route = "/" + str(route)

        self.routes[route] = {'callback': callback, 'methods': methods}

    def delete_route(self, route):
        if not route.startswith("/"):
            route = "/" + str(route)

        del self.routes[route]
