# encoding: utf-8

"""
Example Flask APIServer app.
"""

from flask import Flask, abort, redirect
import apiserver as api

class Person(object):
    def __init__(self, name):
        self.name = name

    def __unicode__(self):
        return self.name
    
    @property
    def properties(self):
        return self.__dict__

class PersonController(api.RESTController):
    route = '/people/<name>/'

    def show(self, name):
        if name not in ['Stan', 'Linn', 'Joseph']:        
            abort(404)
        output = Person(name)
        output.sisters = [Person('Suzanne'), Person('Joanne')]
        output.sisters[1].age = 33
        output.classes = ['Anthropology', 'Econ 101']
        return api.formatted_response(output, html_template='people/person.html', formats=['json', 'yaml', 'html', 'xml'])

    def destroy(self):
        return 'Goodbye world'
