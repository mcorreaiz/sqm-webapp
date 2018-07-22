"""
The flask application package.
"""

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_mongoengine import MongoEngine
from config import get_config
import ssl
import os

app = Flask(__name__)
app.config.from_object(get_config(os.environ.get('DEPLOY_MODE')))

MongoEngine(app) # Inicializa conexion a db
DebugToolbarExtension(app)

import sqmwebapp.views
