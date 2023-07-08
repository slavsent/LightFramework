from quopri import decodestring
from slav_framework.for_request import ParamPostRequests, ParamGetRequests


def not_found_404_view(request):
    return '404 WHAT', '404 PAGE Not Found'


class Framework:
    def __init__(self, routes, fronts):
        self.routes = routes
        self.fronts = fronts

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']

        if not path.endswith('/') and (path[-4:] != 'html'):
            path = f'{path}/'

        if path in self.routes:
            view = self.routes[path]
        else:
            view = not_found_404_view
        request = {}

        method = environ['REQUEST_METHOD']
        request['method'] = method

        if method == 'POST':
            data = ParamPostRequests().get_request_params(environ)
            request['data'] = Framework.decode_value(data)
            print(f'Пришёл post-запрос: {Framework.decode_value(data)}')
        if method == 'GET':
            request_params = ParamGetRequests().get_request_params(environ)
            request['request_params'] = Framework.decode_value(request_params)
            print(f'Пришли GET-параметры:'
                  f' {Framework.decode_value(request_params)}')

        for front in self.fronts:
            front(request)
        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]

    @staticmethod
    def decode_value(data):
        new_data = {}
        for k, v in data.items():
            val = bytes(v.replace('%', '=').replace("+", " "), 'UTF-8')
            val_decode_str = decodestring(val).decode('UTF-8')
            new_data[k] = val_decode_str
        return new_data


# Новый вид WSGI-application.
# Первый — логирующий (такой же, как основной,
# только для каждого запроса выводит информацию
# (тип запроса и параметры) в консоль.
class DebugApplication(Framework):

    def __init__(self, routes_obj, fronts_obj):
        self.application = Framework(routes_obj, fronts_obj)
        super().__init__(routes_obj, fronts_obj)

    def __call__(self, env, start_response):
        print('DEBUG MODE')
        print(env)
        return self.application(env, start_response)


# Новый вид WSGI-application.
# Второй — фейковый (на все запросы пользователя отвечает:
# 200 OK, Hello from Fake).
class FakeApplication(Framework):

    def __init__(self, routes_obj, fronts_obj):
        self.application = Framework(routes_obj, fronts_obj)
        super().__init__(routes_obj, fronts_obj)

    def __call__(self, env, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b'Hello from Fake']
