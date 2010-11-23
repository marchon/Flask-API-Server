# encoding: utf-8

import apiserver as api
import controllers
from flask import Flask, abort
app = Flask(__name__)

# usually, you'd register a module
routes = api.register(controllers, app)

if __name__ == "__main__":
    app.run(debug=True)
