"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, jsonify, make_response
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
        year=datetime.now().year
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
        message=usuarios.to_json()
    )

@app.route('/testgridfs/<filename>')
@app.route('/testgridfs')
def testgridfs(filename=None):
    """For testing purposes"""
    if filename is not None:
        version = mdl.Version.objects.first()
        foto = version.fsid.read()
        # Para descargar notas. Se debiera validar el docx
        r = make_response(foto)
        r.headers.set('Content-Disposition', 'attachment', filename=filename)
        r.headers['Content-Type'] = 'application/octet-stream'
        return r
    version = mdl.Version(redactor=mdl.Usuario.objects.first())
    foto = open('pentakill.png', 'rb')
    version.fsid.put(foto, content_type='image/png')
    version.save()
    return render_template(
        'test.html',
        message="Archivo subido con exito."
    )

@app.route('/testgridfs/retrieve')
def testgridfs_ret():
    """For testing purposes"""
    version = mdl.Version.objects.first()
    foto = version.fsid.read()
    return app.response_class(foto, mimetype='image/png')

@app.route('/testgridfs/download')
def testgridfs_down():
    """For testing purposes"""
    return render_template(
            'download.html'
        )