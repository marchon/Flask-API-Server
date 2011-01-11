# encoding: utf-8

from flask import Request, Response, request, abort
from controllers import RESTController
import hashlib
from functools import wraps

LEVELS = ["public", "restricted", "unrestricted"]

class User(object):
    def __init__(self, userdict):
        self.username = userdict["username"]
        self.password = userdict["password"]
        self.access = {}
        for realm, level in userdict.get("access", {}).items():
            try:
                self.access[realm] = LEVELS.index(level)
            except ValueError:
                raise ValueError("Invalid record for user {user}. {level} is not a proper access level.\
                    Choose one of: {levels}.".format(
                        user=self.username,
                        level=level, 
                        levels=", ".join(LEVELS)
                        ))
    
    def may_see(self, realm, level):
        if isinstance(realm, RESTController):
            realm = realm.realm
        return self.access[realm] >= LEVELS.index(level)
    
    def __eq__(self, other):
        return self.username == other.username and self.password == other.password
        
    def __ne__(self, other):
        return self.username != other.username or self.password != other.password

class AuthenticationMiddleware(object):
    def __init__(self, app, users):
        self.app = app
        self.users = []
        self.usermap = {}
        for user in users:
            user = User(user)
            self.users.append(user)
            self.usermap[user.username] = user

    def allows(self, **current_user):
        user = User(current_user)
        user.password = hashlib.sha224(user.password).hexdigest()
        return user in self.users
    
    def authenticate(self):
        """Sends a 401 response that enables basic auth"""
        return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'})

    def __call__(self, environ, start_response):              
        """
        tests
        print 'USER1' in self.usermap
        print User({'username': 'USER1', 'password': "72127e4f480e4306b6c33689b46f001a33805231926d2f17bac767b1"}) in self.users
        """
                
        request = Request(environ)
        auth = request.authorization

        if not auth or not self.allows(username=auth.username, password=auth.password):
            return self.authenticate()(environ, start_response)
        else:
            environ["user"] = self.usermap[auth.username]
            return self.app(environ, start_response)

class requires(object):
    def __init__(self, realm, level):
        self.realm = realm
        self.level = level
    
    def __call__(self, view):
        @wraps(view)
        def decorated(*vargs, **kwargs):
            if request.environ["user"].may_see(self.realm, self.level):
                return view(*vargs, **kwargs)
            else:
                abort(403)
        return decorated
