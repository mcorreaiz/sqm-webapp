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
    usuario = mdl.Usuario.objects.filter(sigla="JN")[1]
    return render_template(
        'notas.html',
        user = usuario.nombre,
        redacciones = mdl.Nota.objects(redactores__in=[usuario]),
        aprobaciones = mdl.Nota.objects(aprobadores__in=[usuario]),
        comentarios = mdl.Nota.objects(comentadores__in=[usuario])
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
        comentarios = nota.comentarios,
        estados_aprobacion = nota.estados_aprobacion
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

@app.route('/seed')
def seed():
    """Seeds the DB."""
    user1 = mdl.Usuario()
    user1.sigla = "RR"
    user1.nombre = "Ricardo Ramos"
    user1.email = "ricardoramos@sqm.cl"
    user1.save()
    user2 = mdl.Usuario()
    user2.sigla = "JN"
    user2.nombre = "Juan Nestler"
    user2.email = "jjnestler@sqm.cl"
    user2.save()
    user3 = mdl.Usuario()
    user3.sigla = "BG"
    user3.nombre = "Beatriz Garcia"
    user3.email = "bgarcia@sqm.cl"
    user3.save()
    user4 = mdl.Usuario()
    user4.sigla = "GA"
    user4.nombre = "Gonzalo Aguirre"
    user4.email = "gaguirre@sqm.cl"
    user4.save()
    user5 = mdl.Usuario()
    user5.sigla = "GI"
    user5.nombre = "Gerardo Illanes"
    user5.email = "gillanes@sqm.cl"
    user5.save()
    user6 = mdl.Usuario()
    user6.sigla = "PS"
    user6.nombre = "Patricio de Solminihac"
    user6.email = "psolminihac@sqm.cl"
    user6.save()

    version1 = mdl.Version()
    version1.redactor = user1
    version1.nombre = "R_b"
    version1.save()
    version2 = mdl.Version()
    version2.redactor = user2
    version2.nombre = "R_b"
    version2.save()
    version3 = mdl.Version()
    version3.redactor = user3
    version3.nombre = "R_1"
    version3.save()
    version4 = mdl.Version()
    version4.redactor = user4
    version4.nombre = "R_b"
    version4.save()
    version5 = mdl.Version()
    version5.redactor = user5
    version5.nombre = "R_1"
    version5.save()
    version6 = mdl.Version()
    version6.redactor = user6
    version6.nombre = "R_2"
    version6.save()

    #comentario1 = mdl.Comentario()
    #comentario1.redactor = user1
    #comentario1.nombre = "C_1"
    #comentario1.save()
    #comentario2 = mdl.Comentario()
    #comentario2.redactor = user3
    #comentario2.nombre = "C_1"
    #comentario2.save()
    #comentario3 = mdl.Comentario()
    #comentario3.redactor = user5
    #comentario3.nombre = "C_1"
    #comentario3.save()

    nota = mdl.Nota()
    nota.num = "1"
    nota.nombre = "Analisis de Compras"
    nota.redactores = [user1, user2]
    nota.aprobadores = [user3, user4]
    nota.comentadores = [user5, user6]
    nota.estados_aprobacion = {"RR": False, "JN": False, "BG": True, "GA": False}
    nota.ultima_version = 0
    nota.versiones = [version1]
    nota.ultimo_comentario = 0
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "1.1"
    nota.nombre = "Analisis de Ventas"
    nota.redactores = [user3, user4]
    nota.aprobadores = [user5, user6]
    nota.comentadores = [user1, user2]
    nota.estados_aprobacion = {"PS": True, "GI": True, "BG": True, "GA": False}
    nota.ultima_version = 1
    nota.versiones = [version2, version3]
    nota.ultimo_comentario = 0
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "2"
    nota.nombre = "Proyecciones"
    nota.redactores = [user5, user6]
    nota.aprobadores = [user1, user2]
    nota.comentadores = [user3, user4]
    nota.estados_aprobacion = {"RR": False, "JN": False, "GI": False, "PS": True}
    nota.ultima_version = 2
    nota.versiones = [version4, version5, version6]
    nota.ultimo_comentario = 0
    nota.comentarios = []
    nota.save()

    return render_template(
        'main.html',
        title='Todo Ok',
        year=datetime.now().year
    )
