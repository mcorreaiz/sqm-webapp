"""
This script runs the sqmwebapp application using a development server.
"""

from os import environ
from sqmwebapp import app

if __name__ == '__main__':
    app.run(host='0.0.0.0')
