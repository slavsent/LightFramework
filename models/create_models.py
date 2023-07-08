from copy import deepcopy
from quopri import decodestring
from sqlite3 import connect
from utilits.notifier import Subject
from utilits.for_db import DomainObject


class User:
    auto_id = 0

    def __init__(self, name, type_user):
        self.id = User.auto_id
        User.auto_id += 1
        self.name = name
        self.type_user = type_user


class Manager(User, DomainObject):
    def __init__(self, name, type_user):
        self.products = []
        super().__init__(name, type_user)


class Buyer(User, DomainObject):
    def __init__(self, name, type_user):
        self.products = []
        super().__init__(name, type_user)


class OtherPersonal(User, DomainObject):
    def __init__(self, name, type_user):
        self.products = []
        super().__init__(name, type_user)


class UserFactory:
    types = {
        'manager': Manager,
        'buyer': Buyer,
        'other': OtherPersonal,
    }

    @classmethod
    def create(cls, name, type_user):
        if not (type_user in cls.types.keys()):
            type_user = 'other'
        return cls.types[type_user](name, type_user)


class ProductPrototype:

    def clone(self):
        return deepcopy(self)


class Product(ProductPrototype, Subject):

    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.category.products.append(self)
        self.users = []
        super().__init__()

    def __getitem__(self, item):
        return self.users[item]

    def add_user(self, user):
        self.users.append(user)
        user.products.append(self)
        self.notify()

    def rename_product(self, new_name, old_name):
        for i in range(len(self.name)):
            if self.name[i] == old_name:
                self.name[i] = new_name

        self.notify_users()


# грузовые машины
class TruckCar(Product):
    pass


# легковые машины
class Car(Product):
    pass


# легковые машины
class OtherProducts(Product):
    pass


class ProductFactory:
    types = {
        'truckcar': TruckCar,
        'car': Car,
        'other': OtherProducts,
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name, category):
        if not (type_ in cls.types.keys()):
            type_ = 'other'
        return cls.types[type_](name, category)


# категория
class Category(DomainObject):
    auto_id = 0

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.products = []

    def product_count(self):
        result = len(self.products)
        if self.category:
            result += self.category.product_count()
        return result


# основной интерфейс проекта
class Engine:
    def __init__(self):
        self.users = []
        self.buyers = []
        self.other_personal = []
        self.products = []
        self.categories = []

    @staticmethod
    def create_user(name, type_):
        return UserFactory.create(name, type_)

    def get_users(self):
        if len(self.users) > 0:
            for item in self.users:
                return item
        return None

    def get_user(self, name):
        for item in self.users:
            if item.name == name:
                return item

    def find_user_by_id(self, id):
        for item in self.users:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_product(type_, name, category):
        return ProductFactory.create(type_, name, category)

    def get_product(self, name):
        for item in self.products:
            if item.name == name:
                return item
        return None

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return val_decode_str.decode('UTF-8')


class ManagerMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'manager'

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name, type_user = item
            user = Manager(name, type_user)
            user.id = id
            result.append(user)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, name, type_user FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            return Manager(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name, type_user) VALUES (?, ?)"
        self.cursor.execute(statement, (obj.name, obj.type_user, ))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=?, type_user=? WHERE id=?"

        self.cursor.execute(statement, (obj.name, obj.type_user, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


class BuyerMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'buyer'

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name, type_user = item
            user = Manager(name, type_user)
            user.id = id
            result.append(user)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, name, type_user FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            return Manager(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name, type_user) VALUES (?, ?)"
        self.cursor.execute(statement, (obj.name, obj.type_user, ))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=?, type_user=? WHERE id=?"

        self.cursor.execute(statement, (obj.name, obj.type_user, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


class OtherPersonalMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'other_personal'

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name, type_user = item
            user = Manager(name, type_user)
            user.id = id
            result.append(user)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, name, type_user FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            return Manager(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name, type_user) VALUES (?, ?)"
        self.cursor.execute(statement, (obj.name, obj.type_user, ))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=?, type_user=? WHERE id=?"

        self.cursor.execute(statement, (obj.name, obj.type_user, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


class CategoryMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'category'

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name, category = item
            category = Category(name, category)
            category.id = id
            result.append(category)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, name FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            return Manager(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name, category) VALUES (?, ?)"
        self.cursor.execute(statement, (obj.name, obj.category, ))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=?, category=? WHERE id=?"

        self.cursor.execute(statement, (obj.name, obj.category, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


connection = connect('shop.sqlite')


# архитектурный системный паттерн - Data Mapper
class MapperRegistry:
    mappers = {
        'manager': ManagerMapper,
        'buyer': BuyerMapper,
        'other': OtherPersonalMapper,
        'category': CategoryMapper
    }

    @staticmethod
    def get_mapper(obj):

        if isinstance(obj, Manager):
            return ManagerMapper(connection)
        if isinstance(obj, Buyer):
            return BuyerMapper(connection)
        if isinstance(obj, OtherPersonal):
            return OtherPersonalMapper(connection)
        if isinstance(obj, Category):
            return CategoryMapper(connection)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](connection)


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')
