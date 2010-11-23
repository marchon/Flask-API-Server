# encoding: utf-8

from setuptools import setup, find_packages

setup(name='Flask API Server',
        version='0.1',
        description='A minimalistic RESTful multi-format resource server',
        author='Stijn Debrouwere',
        author_email='stijn@stdout.be',
        #url='http://www.ugent.be/',
        packages=find_packages(),
        install_requires=['Flask==0.6', 'simplejson'],
     )
