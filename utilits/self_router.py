from time import time
from jsonpickle import dumps, loads
from logger.logger import Logger, ConsoleWriter
from slav_framework.templator import render


logger_dsl = Logger('my_main', ConsoleWriter())


class SelfRoute:
    def __init__(self, routes, url):
        """
        Инициализация
        :param routes: словарь роутеров
        :param url: адрес url
        """
        self.routes = routes
        self.url = url

    def __call__(self, cls):
        """
        Декоратор
        :param cls: объект класса
        :return:
        """
        self.routes[self.url] = cls()


class TimeDebug:

    def __init__(self, name):
        self.name = name

    def __call__(self, cls):
        """
        Декоратор с параметром
        :param cls:
        :return:
        """

        def timeit(method):
            '''
            Декоратор замеров времени
            '''

            def timed(*args, **kw):
                ts = time()
                result = method(*args, **kw)
                te = time()
                delta = te - ts
                logger_dsl.log(f'Замер функции --> {self.name} выполнялся {delta:2.2f} ms')
                return result

            return timed

        return timeit(cls)


# поведенческий паттерн - Шаблонный метод
class TemplateView:
    template_name = 'base.html'

    def get_context_data(self):
        return {}

    def get_template(self):
        return self.template_name

    def render_template_with_context(self):
        template_name = self.get_template()
        context = self.get_context_data()
        return '200 OK', render(template_name, **context)

    def __call__(self, request):
        return self.render_template_with_context()


class ListView(TemplateView):
    queryset = []
    template_name = 'list.html'
    context_object_name = 'objects_list'

    def get_queryset(self):
        print(self.queryset)
        return self.queryset

    def get_context_object_name(self):
        return self.context_object_name

    def get_context_data(self):
        queryset = self.get_queryset()
        context_object_name = self.get_context_object_name()
        context = {context_object_name: queryset}
        return context


class CreateView(TemplateView):
    template_name = 'create.html'
    queryset = []
    context_object_name = 'objects_list'

    @staticmethod
    def get_request_data(request):
        return request['data']

    def create_obj(self, data):
        pass

    def get_queryset(self):
        print(self.queryset)
        return self.queryset

    def get_context_object_name(self):
        return self.context_object_name

    def get_context_data(self):
        queryset = self.get_queryset()
        context_object_name = self.get_context_object_name()
        context = {context_object_name: queryset}
        return context

    def __call__(self, request):
        if request['method'] == 'POST':

            data = self.get_request_data(request)
            self.create_obj(data)

            return self.render_template_with_context()
        else:
            return super().__call__(request)


class BaseSerializer:

    def __init__(self, obj):
        self.obj = obj

    def save(self):
        return dumps(self.obj)

    @staticmethod
    def load(data):
        return loads(data)
