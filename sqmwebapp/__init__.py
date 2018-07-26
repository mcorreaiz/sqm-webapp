"""
The flask application package.
"""

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_mongoengine import MongoEngine
from flask_oauthlib.client import OAuth, OAuthException
import os

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('sqmwebapp.config')
app.config.from_pyfile('config.py', silent=True)

MongoEngine(app) # Inicializa conexion a db
DebugToolbarExtension(app)
oauth = OAuth(app)

import sqmwebapp.views
