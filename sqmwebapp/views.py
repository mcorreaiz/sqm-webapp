"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, jsonify
from sqmwebapp import app
import sqmwebapp.models as mdl

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/main')
def main():
    """Renders the about page."""
    return render_template(
        'main.html',
        title='Main',
        year=datetime.now().year,
        message='Pagina principal de la App.'
    )

@app.route('/testmongo')
def testmongo():
    """For testing purposes"""
    user = mdl.Usuario()
    user.nombre = 'Matias Correa'
    user.sigla = 'MC'
    user.save()
    usuarios = mdl.Usuario.objects
    return render_template(
        'test.html',
        users=usuarios.to_json(),
        message='Pagina principal de la App.'
    )
