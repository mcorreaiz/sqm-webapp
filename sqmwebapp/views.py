"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, make_response, flash, redirect
from werkzeug.utils import secure_filename
from urllib.parse import unquote

from sqmwebapp import app
import sqmwebapp.utils as u
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

@app.route('/notas')
def notas():
    """Renders the overview of the Notas state."""
    return render_template(
        'notas.html',
        user = "Mutas Pija Chica",
        redacciones = [],
        aprobaciones = [],
        comentarios = []
    )

@app.route('/notas/<num>')
def nota_panel(num):
    """Renders the description of a Nota object."""
    num = unquote(num)
    nota = mdl.Nota.objects.get(num=num)
    return render_template(
        'nota-panel.html',
        num = nota.num,
        nombre = nota.nombre,
        redactores = nota.redactores,
        aprobadores = nota.aprobadores,
        comentadores = nota.comentadores,
        redacciones = nota.versiones,
        comentarios = nota.comentarios
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
@app.route('/testgridfs', methods=['GET', 'POST'])
def testgridfs(filename=None):
    """For testing purposes"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        # If user submits an empty form. TODO: Acivate submit iif selected file
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and u.valid_extension(file.filename):
            filename = secure_filename(file.filename) # Never trust user input
            version = mdl.Version(redactor=mdl.Usuario.objects.first())
            version.fsid.put(file, content_type='application/octet-stream', 
                            filename=filename)
            version.save()
            return render_template(
                'test.html',
                message="Archivo subido con exito."
            )
		

    if filename is not None:
        version = mdl.Version.objects.order_by('-fecha').first() # Query the newest
        doc = version.fsid
        down = u.download_file(doc)
        return down if down else render_template(
            'test.html',
            message="Nada que hacer por hoy."
        )
    else:
        return render_template(
            'test.html',
            message="Nada que hacer por hoy."
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
