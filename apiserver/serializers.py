# encoding: utf-8

import simplejson
import yaml
from flask import render_template

"""
Objects may specify a 'facade' property, which will be used instead of its public properties
when serializing the object. This attribute may be a list or a string, but is most often a 
dictionary, e.g. a subset of self.__dict__. The simplest implementation is as follows:

class MyClass(object):
    @property
    def facade(self):
        return self.__dict__
"""

"""
Prior to serialization, we recursively simplify the object structure to the lowest common denominator,
that is, everything that is easily representable in JSON. That way, we can make sure that the output
of each serialization format will stay close to the other formats, making it easy for users to switch
between formats, and easy for us to document our API without having to explain differences in how each
format renders the same resource.
"""

class Simplifier(object):
    def simplify_list(self, obj):
        simplify = self.__class__()
        return [simplify(item) for item in obj]
    
    def simplify_dict(self, obj):
        simplify = self.__class__()
        simple = {}
        for key, value in obj.items():
            simple[key] = simplify(value)
        return simple
    
    def simplify_tuple(self, obj):
        return list(obj)
    
    def simplify_string(self, obj):
        try:
            return unicode(obj)
        except UnicodeDecodeError:
            return obj
        
    def simplify_object(self, obj):
        if hasattr(obj, 'facade'):
            facade = obj.facade
        else:
            attrs =  obj.__dict__
            for attr in attrs.keys():
                if attr.startswith('_'):
                    del attrs[attr]
            facade = attrs
            
        facade = self.simplify_dict(facade)
        
        return {obj.__class__.__name__.lower(): facade}
    
    def __call__(self, obj):
        if isinstance(obj, list):
            return self.simplify_list(obj)
        elif isinstance(obj, dict):
            return self.simplify_dict(obj)
        elif isinstance(obj, tuple):
            return self.simplify_tuple(obj)
        elif isinstance(obj, str):
            return self.simplify_string(obj)
        elif hasattr(obj, '__dict__'):
            return self.simplify_object(obj)
        else:
            return obj

simplify = Simplifier()

class Resource(object):
    def __init__(self, obj):
        self.obj = obj

    # dead-simple serialization, because we want XML  
    # that completely mirrors the JSON output
    # (no attributes or other fancy stuff)        
    def to_xml(self, parent='item', depth=0):   
        out = ''
        simple = True
    
        if isinstance(self.obj, list):
            simple = False
            out += '\n'
            if parent == 'item':
                parent = 'list'
            for item in self.obj:
                out += Resource(item).to_xml('item', depth+1)
        elif isinstance(self.obj, dict):
            simple = False
            out += '\n'
            for key, value in self.obj.items():
                out += Resource(value).to_xml(key, depth+1)
        else:
            out += unicode(self.obj)
        
        start_tabs = end_tabs = ''
        for i in range(depth):
            start_tabs += '    '
        if not simple:
            end_tabs = start_tabs
        return '{0}<{1}>{2}{3}</{1}>\n'.format(start_tabs, parent, out, end_tabs)
        
    def to_json(self):
        return simplejson.dumps(self.obj, indent=4)
    
    def to_html(self, template):
        return render_template(template, **self.obj.__dict__)
    
    def to_yaml(self):
        def unicode_representer(dumper, data):
            return yaml.ScalarNode('tag:yaml.org,2002:str', data)
    
        yaml.add_representer(unicode, unicode_representer)
        return yaml.dump(self.obj, default_flow_style=False)
    
    def to_txt(self):
        return unicode(self.obj)

def formatted_response(obj, html_template=None, formats=['xml', 'json', 'yaml']):
    simple_obj = simplify(obj)
    resource = Resource(simple_obj)
    formatters = {
        'xml': resource.to_xml, 
        'json': resource.to_json, 
        'txt': resource.to_txt, 
        'yaml': resource.to_yaml, 
        'html': lambda: resource.to_html(html_template), 
    }

    for formatter in formatters.keys():
        if formatter not in formats:
            del formatters[formatter]

    return formatters

"""
Tests (todo: convert to proper unit tests)

class Fancy(object):
    def __init__(self):
        self.funicode = u'some name'
        self.fstring = 'mr'
        self.flist = ['one', 'two', 'three']
        self.ftuple = ('one', 'three', 'five')
        self.fdict = {'one': 1, 'two': 2}
        self._private = 'private'
        
        @property
        def facade(self):
            return self.__dict__

from pprint import pprint

f = Fancy()
f.deep = [Fancy(), Fancy(), 'unfancy']
        
simplify = Simplifier()
simple_f = simplify(f)

resource = Resource([simple_f])
pprint(simple_f)
print simplejson.dumps(simple_f, indent=4)
print(resource.to_yaml())
"""
