from datetime import date
from slav_framework.templator import render
from logger.logger import Logger, FileWriter, ConsoleWriter
from models.create_models import Engine, MapperRegistry
from utilits.self_router import SelfRoute, TimeDebug, ListView, CreateView, BaseSerializer
from utilits.notifier import EmailNotifier, SmsNotifier, EmailNotifierUsers, SmsNotifierUsers
from utilits.for_db import UnitOfWork


site = Engine()
logger_dsl = Logger('my_main', ConsoleWriter())
logger = Logger('main', FileWriter())
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()
email_notifier_user = EmailNotifierUsers()
sms_notifier_user = SmsNotifierUsers()
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)


class About:
    def __call__(self, request):
        return '200 OK', 'about'


routes = {
    '/about/': About(),
}


@SelfRoute(routes=routes, url='/create-user/')
class CreateUser(CreateView):
    #queryset = site.users
    template_name = 'create_user.html'

    def create_obj(self, data: dict):
        name = data['your_name']
        name = site.decode_value(name)
        type_user = data['type_user']
        type_user = site.decode_value(type_user)
        new_obj = site.create_user(name, type_user)
        site.users.append(new_obj)
        new_obj.mark_new()
        UnitOfWork.get_current().commit()

    def get_queryset(self):
        mapper_manager = MapperRegistry.get_current_mapper('manager')
        mapper_buyer = MapperRegistry.get_current_mapper('buyer')
        mapper_other = MapperRegistry.get_current_mapper('other')
        if len(site.users) == 0:
            data_personal = mapper_manager.all() + mapper_buyer.all() + mapper_other.all()
            for item in data_personal:
                site.users.append(item)
        return site.users


"""
# контроллер - создать пользователя
@SelfRoute(routes=routes, url='/create-user/')
class CreateUser:
    @TimeDebug(name='CreateUser')
    def __call__(self, request):

        if request['method'] == 'POST':

            data = request['data']
            # print(data)
            name = data['your_name']
            name = site.decode_value(name)
            type_user = data['type_user']
            type_user = site.decode_value(type_user)

            new_user = site.create_user(name, type_user)

            site.users.append(new_user)
            logger.log('Добавлен пользователь')
            logger_dsl.log('Добавлен пользователь')
            return '200 OK', render('another_page.html', objects_list=site.users)
        else:
            users = site.users
            logger.log('Список пользователей')
            return '200 OK', render('create_user.html',
                                    objects_list=users)
"""


@SelfRoute(routes=routes, url='/users/')
class Another(ListView):
    logger.log('Список пользователей')
    #queryset = site.users
    template_name = 'another_page.html'

    # def __call__(self, request):
    #    logger.log('Список пользователей')
    # return '200 OK', render('another_page.html', objects_list=site.users)

    def get_queryset(self):
        mapper_manager = MapperRegistry.get_current_mapper('manager')
        mapper_buyer = MapperRegistry.get_current_mapper('buyer')
        mapper_other = MapperRegistry.get_current_mapper('other')
        if len(site.users) == 0:
            data_personal = mapper_manager.all()+mapper_buyer.all()+mapper_other.all()
            for item in data_personal:
                site.users.append(item)
        return site.users


@SelfRoute(routes=routes, url='/')
class Index:
    def __call__(self, request):
        return '200 OK', render('index.html', date=request.get('date', None))


@SelfRoute(routes=routes, url='/contact/')
class Contact:
    def __call__(self, request):
        return '200 OK', render('contact.html')


@SelfRoute(routes=routes, url='/examples/')
class Examples:
    def __call__(self, request):
        return '200 OK', render('examples.html', date=request.get('date', None))


@SelfRoute(routes=routes, url='/products/')
class Page(ListView):
    logger.log('Список категорий товаров')
    logger_dsl.log('Список категорий товаров')
    template_name = 'page.html'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('category')
        if len(site.categories) == 0:
            data_category = mapper.all()
            for item in data_category:
                site.categories.append(item)
        return site.categories

    #def __call__(self, request):
    #    logger.log('Список категорий товаров')
    #    logger_dsl.log('Список категорий товаров')
    #    return '200 OK', render('page.html', objects_list=site.categories)


# контроллер - создать категорию
@SelfRoute(routes=routes, url='/create-category/')
class CreateCategory:
    @TimeDebug(name='CreateCategory')
    def __call__(self, request):

        if request['method'] == 'POST':
            # метод пост

            data = request['data']

            name = data['category_name']
            name = site.decode_value(name)

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)

            site.categories.append(new_category)
            new_category.mark_new()
            UnitOfWork.get_current().commit()
            logger.log('Добавлена категория товаров')
            return '200 OK', render('page.html', objects_list=site.categories)
        else:
            logger.log('Список категорий товаров')
            categories = site.categories
            return '200 OK', render('create_category.html', objects_list=categories)


# @SelfRoute(routes=routes, url='/about/')
# class About:
#    def __call__(self, request):
#        return '200 OK', 'about'


# контроллер - список товаров
@SelfRoute(routes=routes, url='/product-list/')
class ListProduct:
    def __call__(self, request):
        logger.log('Список товаров')
        try:
            category = site.find_category_by_id(
                int(request['request_params']['id']))
            return '200 OK', render('list_product.html',
                                    objects_list=category.products,
                                    name=category.name, id=category.id)
        except KeyError:
            return '200 OK', 'No product have been added yet'


# контроллер - создать товар
@SelfRoute(routes=routes, url='/create-product/')
class CreateProduct:
    category_id = -1

    @TimeDebug(name='CreateProduct')
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']

            name = data['product_name']
            name = site.decode_value(name)

            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))

                # product = site.create_product('other', name, category)
                product = site.create_product(category.name, name, category)
                site.products.append(product)

                product.observers.append(email_notifier)
                product.observers.append(sms_notifier)

            return '200 OK', render('list_product.html',
                                    objects_list=category.products,
                                    name=category.name,
                                    id=category.id)

        else:
            try:
                self.category_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.category_id))
                return '200 OK', render('create_product.html',
                                        objects_list=category.products,
                                        name=category.name,
                                        id=category.id)
            except KeyError:
                return '200 OK', 'No categories have been added yet'


# контроллер - копировать товар
@SelfRoute(routes=routes, url='/copy-product/')
class CopyProduct:
    def __call__(self, request):
        request_params = request['request_params']

        try:
            name = request_params['name']
            id_category = int(request_params['id'])
            old_product = site.get_product(name)
            if old_product:
                new_name = f'copy_{name}_1'
                new_product = old_product.clone()
                new_product.name = new_name
                site.products.append(new_product)

            return '200 OK', render('list_product.html',
                                    objects_list=site.products,
                                    name=new_product.category.name,
                                    id=id_category,
                                    )
        except KeyError:
            return '200 OK', 'No product have been added yet'


@SelfRoute(routes=routes, url='/add-product-user/')
class AddUserByProductCreateView(CreateView):
    template_name = 'add_products_users.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['products'] = site.products
        context['users'] = site.users
        return context

    def create_obj(self, data: dict):
        product_name = data['product_name']
        product_name = site.decode_value(product_name)
        product = site.get_product(product_name)
        user_name = data['user_name']
        user_name = site.decode_value(user_name)
        user = site.get_user(user_name)
        product.add_user(user)
        product.observers.append(email_notifier_user)
        product.observers.append(sms_notifier_user)


@SelfRoute(routes=routes, url='/api/')
class CourseApi:
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.products).save()


@SelfRoute(routes=routes, url='/rename-product/')
class RenameProduct:
    category_id = -1
    old_name_product = ''

    @TimeDebug(name='RenameProduct')
    def __call__(self, request):

        if request['method'] == 'POST':
            data = request['data']

            name_new = data['product_name']
            name_new = site.decode_value(name_new)

            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))

                product = site.get_product(self.old_name_product)
                product.name = name_new
                product.rename_product(name_new, self.old_name_product)

            return '200 OK', render('list_product.html',
                                    objects_list=category.products,
                                    name=category.name,
                                    id=category.id)

        else:
            try:
                self.category_id = int(request['request_params']['id'])
                name_product = request['request_params']['name']
                self.old_name_product = name_product
                category = site.find_category_by_id(int(self.category_id))
                return '200 OK', render('rename_product.html',
                                        objects_list=category.products,
                                        name=category.name,
                                        id=category.id,
                                        name_product=name_product)
            except KeyError:
                return '200 OK', 'No categories have been added yet'
