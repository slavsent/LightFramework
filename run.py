from wsgiref.simple_server import make_server
from slav_framework.main import Framework, DebugApplication, FakeApplication

from urls import fronts
from views import routes

app = Framework(routes, fronts)
#app = FakeApplication(routes, fronts)
#app = DebugApplication(routes, fronts)

with make_server('', 8000, app) as httpd:
    print("Run server, port: 8000")
    httpd.serve_forever()
