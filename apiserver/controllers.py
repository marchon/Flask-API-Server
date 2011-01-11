# encoding: utf-8

from flask import abort
import dispatch
import inspect

# a Railsy REST controller
class RESTController(object):
    @property
    def methods(self):
        return {
            'GET': getattr(self, 'show', None),
            'POST': getattr(self, 'create', None),
            'PUT': getattr(self, 'update', None),
            'DELETE': getattr(self, 'destroy', None),           
        }

    def __init__(self, app):
        route = self.route.rstrip('/') + '.<format>'
        available_methods = [method for method in self.methods if self.methods[method] is not None]

        self.responds_to = []
        for method in available_methods:
            name = self.__class__.__name__ + "#" + self.methods[method].__name__
            route_with_method = '{0} {1}'.format(method, route)
            self.responds_to.append(route_with_method)
            print 'Registered {0} for {1}'.format(route_with_method, name)
            app.add_url_rule(
                route, 
                name, 
                view_func=dispatch.format_dispatcher(app, self.methods[method]), 
                methods=[method]
                )

def register(module, app):
    controllers = [obj for name, obj in inspect.getmembers(module)
        if inspect.isclass(obj)
        and issubclass(obj, RESTController)]
        
    routes = []
    for controller in controllers:
        controller = controller(app)
        routes += controller.responds_to
    
    return routes
