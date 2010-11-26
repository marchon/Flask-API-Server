# encoding: utf-8

"""
Example Flask APIServer app.
"""

from flask import Flask, request, abort, redirect
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
    route = '/people/<name>'
    realm = 'people'

    def show(self, name):
        user = request.environ["user"]

        if name not in ['Stan', 'Linn', 'Joseph']:        
            abort(404)
        output = Person(name)
        # don't show personal information to any joe schmoe
        if user.may_see(self, "restricted"):
            output.sisters = [Person('Suzanne'), Person('Joanne')]
            output.sisters[1].age = 33
        output.classes = ['Anthropology', 'Econ 101']
        return api.formatted_response(output, html_template='people/person.html', formats=['json', 'yaml', 'html', 'xml'])

    def destroy(self):
        return 'Goodbye world'

class PeopleController(api.RESTController):
    route = '/people'
    realm = 'people'
    
    @api.requires(realm, "unrestricted")
    def show(self):
        return api.formatted_response({})