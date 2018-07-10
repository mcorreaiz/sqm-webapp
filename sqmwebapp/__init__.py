"""
The flask application package.
"""

from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

db = MongoEngine(app)
app.config['MONGODB_DB'] = 'project1'
app.config['MONGODB_HOST'] = '192.168.1.35'
app.config['MONGODB_PORT'] = 12345
app.config['MONGODB_USERNAME'] = 'webapp'
app.config['MONGODB_PASSWORD'] = 'pwd123'

import sqmwebapp.views
