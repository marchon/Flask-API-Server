# encoding: utf-8

import simplejson
import yaml
from flask import render_template

"""
The resource serializer depends on a 'properties' attribute when serializing objects, 
both for XML and JSON. This attribute should be a dictionary. The simplest implementation
is as follows:

class MyClass(object):
    @property
    def properties(self):
        return self.__dict__
        
If I ever get around to refactoring this, a better approach to the serialization would to
objects --> dumbed-down representation (strings, dicts, lists) --> serialize
"""

class Resource(object):
    def __init__(self, obj):
        self.obj = obj

    # dead-simple serialization, because pyxser is a bit over the top
    # and because we want XML that completely mirrors the JSON output
    # (so no attributes or other fancy stuff)
    def to_xml(self, parent='item'):
        out = ''
        
        if isinstance(self.obj, list) or isinstance(self.obj, tuple):
            for item in self.obj:
                out += Resource(item).to_xml()
            return '<{0}>{1}</{0}>'.format(parent, out)
        elif isinstance(self.obj, dict):
            for attr in self.obj:
                prop = self.obj[attr]
                out += Resource(prop).to_xml(attr)
            return '<{0}>{1}</{0}>'.format('item', out)            
        elif hasattr(self.obj, 'properties'):
            name = self.obj.__class__.__name__.lower()
            for attr in self.obj.properties:
                prop = self.obj.properties[attr]
                out += Resource(prop).to_xml(attr)
            return '<{0}>{1}</{0}>'.format(name, out)
        else:
            return '<{0}>{1}</{0}>'.format(parent, self.obj)
        
    def to_json(self):
        def object_encoder(obj):
            if hasattr(obj, 'properties'):
                return obj.properties
            raise TypeError(repr(obj) + " is not JSON serializable")  
        return simplejson.dumps(self.obj, default=object_encoder, indent=4)
    
    def to_html(self, template):
        return render_template(template, **self.obj.__dict__)
    
    def to_yaml(self):
        def obj_representer(dumper, data):
            return dumper.represent_mapping('tag:yaml.org,2002:map', data.properties)
        def unicode_representer(dumper, data):
            return yaml.ScalarNode('tag:yaml.org,2002:str', data)
    
        yaml.add_representer(unicode, unicode_representer)
        if hasattr(self.obj, 'properties'):
            yaml.add_representer(self.obj.__class__, obj_representer)
        return yaml.dump(self.obj, default_flow_style=False)
    
    def to_txt(self):
        return unicode(self.obj)

def formatted_response(obj, html_template=None, formats=['xml', 'json', 'yaml']):
    resource = Resource(obj)
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
