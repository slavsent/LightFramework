from datetime import date


# from views import Index, Contact, Another, Examples, Page, About, CreateUser, CreateCategory, ListProduct, \
#    CreateProduct, CopyProduct


# front controller
def secret_front(request):
    request['date'] = date.today()


def other_front(request):
    request['key'] = 'key'


fronts = [secret_front, other_front]

"""
routes = {
    '/': Index(),
    '/contact/': Contact(),
    '/users/': Another(),
    '/examples/': Examples(),
    '/products/': Page(),
    '/about/': About(),
    '/create-user/': CreateUser(),
    '/create-category/': CreateCategory(),
    '/product-list/': ListProduct(),
    '/create-product/': CreateProduct(),
    '/copy-product/': CopyProduct(),
}
"""
