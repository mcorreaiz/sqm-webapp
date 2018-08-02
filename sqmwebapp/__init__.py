"""
The flask application package.
"""

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_mongoengine import MongoEngine
import os

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('sqmwebapp.config')
app.config.from_pyfile('config.py', silent=True)

MongoEngine(app) # Inicializa conexion a db
DebugToolbarExtension(app)

import sqmwebapp.views
