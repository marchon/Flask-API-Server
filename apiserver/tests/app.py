# encoding: utf-8

import yaml
import apiserver as api
import controllers
from flask import Flask, abort
app = Flask(__name__)

# you may register any dictionary containing RESTControllers as values, 
# but registering an entire module, as we do here, is often handiest
routes = api.register(controllers, app)

userdata = open("users.yaml").read()
users = yaml.load_all(userdata)
users = list(users)

if __name__ == "__main__":
    app.wsgi_app = api.AuthenticationMiddleware(app.wsgi_app, users)
    app.run(debug=True)