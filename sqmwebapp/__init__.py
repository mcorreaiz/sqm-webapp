"""
The flask application package.
"""

from flask import Flask
from flask_mongoengine import MongoEngine
import ssl

DB_URI = 'mongodb://mcorreaiz:zbcI6fmYSvC1pOIufP2gYzo9Gk2O5UCDVH87T8zTrocEj8NpvWeQgeXS3aDIZLRzGx9Oa2zBsVOjWPk8fO5nfA==@mcorreaiz.documents.azure.com:10255/dev?ssl=true&replicaSet=globaldb'
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['MONGODB_SETTINGS'] = {
    'host' : DB_URI,
    'ssl' : True,
    'ssl_cert_reqs' : ssl.CERT_NONE
}
app.debug = True
db = MongoEngine(app)

import sqmwebapp.views

