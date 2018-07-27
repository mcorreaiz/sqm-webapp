"""
Routes and views for the flask application.
"""

import uuid
from datetime import datetime

import requests
from flask import (flash, jsonify, make_response, redirect, render_template,
                   request, session, url_for, g)
from werkzeug.utils import secure_filename
from urllib.parse import unquote

import sqmwebapp.models as mdl
import sqmwebapp.utils as utl
from sqmwebapp import app

@app.before_request
def register():
    if 'user' not in session: # Not registered with DB
        # Lazy auth
        user = utl.get_user_via_headers(request.headers)
        if user is None: # New user, or header failed somehow
            data = me()
            if not data.get_json(): # Empty body means the API requires new auth
                return redirect('https://{}/.auth/logout'.format(app.config['APP_URL']))
            user = utl.get_or_create_user_via_api(data.get_json())
        session['user'] = user.nombre
        session['user_id'] = user.user_id

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    return redirect('https://{}/.auth/logout'.format(app.config['APP_URL']))

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Homee Page',
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
    print(session['user'])
    usuario = mdl.Usuario.objects.get(user_id=session['user'])
    return render_template(
        'notas.html',
        user = usuario.nombre,
        user_id = usuario.user_id,
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
        estados_aprobacion = nota.estados_aprobacion,
        user = mdl.Usuario.objects.get(nombre=session['user'])
    )

@app.route('/testmongo')
def testmongo():
    """For testing purposes"""
    user = mdl.Usuario()
    user.nombre = 'Matias Correa'
    user.user_id = '123456qwerty'
    user.email = 'yo@aaa.aaa'
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

        if file and utl.valid_extension(file.filename):
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
        version = mdl.Nota.objects(num=num).versiones[-1] # Query the newest
        doc = version.fsid
        down = utl.download_file(doc)
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
    user1.nombre = "Ricardo Ramos"
    user1.email = "ricardoramos@sqm.cl"
    user1.user_id = "1"
    user1.save()
    user2 = mdl.Usuario()
    user2.nombre = "Juan Nestler"
    user2.email = "jjnestler@sqm.cl"
    user2.user_id = "7e5b5d5e-e151-4e78-a6b8-ea0dcbc0d3fd"
    user2.save()
    user3 = mdl.Usuario()
    user3.nombre = "Beatriz Garcia"
    user3.email = "bgarcia@sqm.cl"
    user3.user_id = "2"
    user3.save()
    user4 = mdl.Usuario()
    user4.nombre = "Gonzalo Aguirre"
    user4.email = "gaguirre@sqm.cl"
    user4.user_id = "3"
    user4.save()
    user5 = mdl.Usuario()
    user5.nombre = "Gerardo Illanes"
    user5.email = "gillanes@sqm.cl"
    user5.user_id = "4"
    user5.save()
    user6 = mdl.Usuario()
    user6.nombre = "Patricio de Solminihac"
    user6.email = "psolminihac@sqm.cl"
    user6.user_id = "5"
    user6.save()
    user7 = mdl.Usuario()
    user7.nombre = "Matias Correa"
    user7.email = "mcorrea@sqm.cl"
    user7.user_id = "f0a69c76-d294-4a9a-b43f-8a23dba60b45"
    user7.save()

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

    comentario1 = mdl.Comentario()
    comentario1.redactor = user1
    comentario1.contenido = "Se subio versión base equivocada"
    comentario1.nombre = "C_1"
    comentario1.save()
    comentario2 = mdl.Comentario()
    comentario2.redactor = user3
    comentario2.contenido = "Figura 3 esta girada"
    comentario2.nombre = "C_1"
    comentario2.save()
    comentario3 = mdl.Comentario()
    comentario3.redactor = user5
    comentario3.contenido = "Cambiar linea 5, la redacción es erronea"
    comentario3.nombre = "C_1"
    comentario3.save()

    nota = mdl.Nota()
    nota.num = "1"
    nota.nombre = "Analisis de Compras"
    nota.redactores = [user1, user2, user7]
    nota.aprobadores = [user3, user4]
    nota.comentadores = [user5, user6]
    nota.estados_aprobacion = {user1.user_id: True, user2.user_id: True, user7.user_id: True, user3.user_id: True, user4.user_id: True}
    nota.versiones = [version1]
    nota.comentarios = [comentario1]
    nota.save()

    nota = mdl.Nota()
    nota.num = "1.1"
    nota.nombre = "Analisis de Ventas"
    nota.redactores = [user3, user4]
    nota.aprobadores = [user5, user6, user7]
    nota.comentadores = [user1, user2]
    nota.estados_aprobacion = {user3.user_id: True, user4.user_id: False, user5.user_id: True, user6.user_id: False, user7.user_id: False}
    nota.versiones = [version2, version3]
    nota.comentarios = [comentario2]
    nota.save()

    nota = mdl.Nota()
    nota.num = "2"
    nota.nombre = "Proyecciones"
    nota.redactores = [user5, user6]
    nota.aprobadores = [user1, user2]
    nota.comentadores = [user3, user4, user7]
    nota.estados_aprobacion = {user5.user_id: False, user6.user_id: False, user1.user_id: False, user2.user_id: True}
    nota.versiones = [version4, version5, version6]
    nota.comentarios = [comentario3]
    nota.save()

    return render_template(
        'main.html',
        title='Todo Ok',
        year=datetime.now().year
    )

@app.route('/headers')
def headers():
    print(request.cookies)
    """For testing purposes"""
    return render_template(
            'test.html',
            message=request.headers
        )

@app.route('/me') # TODO: remove decorator and move to utils
def me():
    """For testing purposes"""
    access_token = request.headers.get(utl.ACCESS_TOKEN_HEADER)

    if utl.running_localhost(request):
        r = requests.get('https://{}/.auth/me'.format(app.config['APP_URL']), cookies={utl.AZURE_COOKIE_NAME:utl.COOKIE_VALUE})
        body = r.json()
        return jsonify(utl.parse_auth_claims(body[0]['user_claims']))

    if not access_token: # Logout required
        return make_response() #Empty response

    r = requests.get('https://{}/.auth/me'.format(app.config['APP_URL']), headers={'Authorization':'Bearer '+access_token})
    body = r.json()

    if r.status_code == 401 or not body: # Access token expired or error
        return make_response() #Empty response
        
    return jsonify(utl.parse_auth_claims(body[0]['user_claims']))

# TODO sprint: Viste notas completa con cargar/descargar veriones. Sitema de aprobaciones. Poder leer y escribir comentarios.