# encoding: utf-8

from flask import request, abort
import types
from functools import wraps
import utils

MIMETYPES = {
    'json': 'application/json',
    'xml':  'text/xml',
    'txt': 'text/plain',
    'yaml': 'text/yaml',
    'html': 'text/html',
    }

"""
This code is a bit cryptic by itself. See :func:`formatted_response` in serializers.py
and the initialization routine of the RESTController (controllers.py) to get a better 
grasp of how this fits into the code flow.

In a nutshell, it works like this: 
1. we define a view (e.g. the method `show` on a RESTController subclass)
2. we render the view by passing a python object to formatted_response
3. formatted_response returns a dictionary of possible formats, and the functions
   that render each specific format (using serializers)
4. format_dispatcher, which wraps our view, inspecting the request, decides
   which format the user wishes for, selects it from the dictionary returned by
   formatted_response, executes it, sets the appropriate mimetype and then returns
   the response.
"""

def format_dispatcher(app, view):
    @utils.timed()
    def format_aware_view(**kwargs):
        format = kwargs['format']
        request.format = format
        del kwargs['format']
        initialized_view = view(**kwargs)
        if format not in initialized_view:
            abort(404)
        rendered_view = initialized_view[format]()
        response = app.make_response(rendered_view)
        response.mimetype = MIMETYPES[format]
        return response
    return format_aware_view

"""
An error handling decorator. Usage:

@on_error(NoObjectsFound, 404)
@on_error(IOError, 503)
def my_view():
    raise IOError("Database down for maintenance")
    
Works on RESTController classes as well, in which case
the class decorator will decorate the 'show', 'create', 
'update' and 'destroy' methods.
"""

class on_error(object):
    def __init__(self, exception, code):
        self.exception = exception
        self.code = code

    def decorate_fn(self, fn):
        @wraps(fn)
        def safe_fn(*vargs, **kwargs):
            try:
                return fn(*vargs, **kwargs)
            except self.exception:
                abort(self.code)
                
        return safe_fn
        
    def decorate_cls(self, cls):
        for name in ['show', 'create', 'update', 'destroy']:
            if hasattr(cls, name):
                method = getattr(cls, name)
                setattr(cls, name, self.decorate_fn(method))
        return cls

    def __call__(self, obj):
        if isinstance(obj, types.FunctionType):
            return self.decorate_fn(obj)
        else:
            return self.decorate_cls(obj)
