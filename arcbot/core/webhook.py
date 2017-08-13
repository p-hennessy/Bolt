from gevent.pywsgi import WSGIServer
import gevent

class WebhookManager():
    def __init__(self):
        pass

    def start(self):
        gevent.sleep(0)

class Webserver():
    def __init__(self):
        self.routes = {}
        self.server = WSGIServer(('', 8080), self.app)

    def start(self):
        pass
        #self.server.serve_forever()

    def ping(self, request):
        print('Ping recived')

    def app(self, env, response):
        route = env['PATH_INFO']
        method = env['REQUEST_METHOD']

        if route not in self.routes.keys():
            status = '404 NOT FOUND'
            response(status, [])
            return ['']

        route_data = self.routes[route]

        if method not in route_data['methods']:
            status = '405 METHOD NOT ALLOWED'
            response(status, [])
            return ['']

        status = '200 OK'
        response(status, [])
        return ['']

    def add_route(self, route, callback, methods=['GET']):
        if not route.startswith("/"):
            route = "/" + str(route)

        self.routes[route] = {'callback': callback, 'methods': methods}

    def delete_route(self, route):
        if not route.startswith("/"):
            route = "/" + str(route)

        del self.routes[route]

class Request():
    def __init__(route, method, body='', headers=[], data={}):
        pass

class Response():
    def __init__(code, body='', headers=[], data={}):
        pass
