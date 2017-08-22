from gevent.pywsgi import WSGIServer
import logging
import ujson as json
import falcon

class WebhookServer():
    def __init__(self):
        self.routes = {}
        self.app = falcon.API()
        self.app.add_sink(self.handle, '/')

        self.server = WSGIServer(('', 8080), self.app)
        self.logger = logging.getLogger(__name__)

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
            print(e)
            response.status = falcon.HTTP_500

    def add_route(self, route, callback, methods=['GET']):
        if not route.startswith("/"):
            route = "/" + str(route)

        self.routes[route] = {'callback': callback, 'methods': methods}

    def delete_route(self, route):
        if not route.startswith("/"):
            route = "/" + str(route)

        del self.routes[route]


#@webhook('/', methods=['GET'])
def example(request):
    data = json.loads(request.stream.read())
    channel_id = '249770653534650378'
    message = "New commit: {}"

    import pdb; pdb.set_trace()
