"""
Routes and views for the flask application.
"""

import uuid
import zipfile
from datetime import datetime
from docx import Document
from io import BytesIO

import requests
from flask import (flash, jsonify, make_response, redirect, render_template,
                   request, session, url_for, g, send_file)
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

@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Homee Page',
        year=datetime.now().year,
    )

@app.route('/')
def notas():
    """Renders the overview of the Notas state."""
    usuario = mdl.Usuario.objects.get(user_id=session['user_id'])
    return render_template(
        'notas.html',
        user = usuario,
        redacciones = mdl.Nota.objects(redactores__in=[usuario]),
        aprobaciones = mdl.Nota.objects(aprobadores__in=[usuario]),
        comentarios = mdl.Nota.objects(comentadores__in=[usuario])
    )

@app.route('/notas/<num>', methods=['GET', 'POST'])
def nota_panel(num):
    """Renders the description of a Nota object."""
    num = unquote(num)
    nota = mdl.Nota.objects.get(num=num)

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Ningun archivo seleccionado', 'error')
            return redirect(request.url)

        file = request.files['file']

        # If user submits an empty form. TODO: Acivate submit iif selected file
        if file.filename == '':
            flash('Ningun archivo seleccionado', 'error')

        if file and utl.valid_extension(file.filename):
            filename = secure_filename(file.filename) # Never trust user input
            redactor = mdl.Usuario.objects.get(user_id=session['user_id'])
            nombre_creacion = "{0}_{1}".format(redactor.iniciales, datetime.now().strftime('%m_%d'))
            contenido = request.form.get('comentario')
            comentario = mdl.Comentario(contenido=contenido,
                                        redactor=redactor,
                                        nombre="C_0",
                                        nombre_creacion=nombre_creacion)
            comentario.save()

            version = mdl.Version(redactor=redactor)
            version.archivo.put(file, content_type='application/octet-stream', 
                            filename=filename)
            if len(nota.versiones) == 0:
                version.nombre = "R_b"
            else:
                version.nombre = "R_{}{}".format(len(nota.versiones), 'b' if request.form.get('borrador') else '')
            version.nombre_creacion = nombre_creacion
            version.comentarios = [comentario]
            version.save()
            nota.versiones.append(version)
            for user in nota.estados_aprobacion.keys():
                nota.estados_aprobacion[user] = False
            nota.save()
            flash('Version subida con exito', 'success')
        else:
            flash('Version no subida; extension invalida', 'error')

        return redirect(request.url)

    return render_template(
        'nota-panel.html',
        nota = nota,
        user = mdl.Usuario.objects.get(user_id=session['user_id']),
        version = nota.versiones[-1] if nota.versiones else mdl.Version(nombre_creacion="No hay versiones", nombre="")
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

    nota = mdl.Nota()
    nota.num = "1"
    nota.nombre = "Analisis de Compras"
    nota.redactores = [user1, user2, user7]
    nota.aprobadores = [user3, user4]
    nota.comentadores = [user5, user6]
    nota.estados_aprobacion = {user1.user_id: True, user2.user_id: True, user7.user_id: True, user3.user_id: True, user4.user_id: True}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "1.1"
    nota.nombre = "Analisis de Ventas"
    nota.redactores = [user3, user4]
    nota.aprobadores = [user5, user6, user7]
    nota.comentadores = [user1, user2]
    nota.estados_aprobacion = {user3.user_id: True, user4.user_id: False, user5.user_id: True, user6.user_id: False, user7.user_id: False}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "2"
    nota.nombre = "Proyecciones"
    nota.redactores = [user5, user6]
    nota.aprobadores = [user1, user2]
    nota.comentadores = [user3, user4, user7]
    nota.estados_aprobacion = {user5.user_id: False, user6.user_id: False, user1.user_id: False, user2.user_id: True}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "3"
    nota.nombre = "Produccion Nacional"
    nota.redactores = [user1, user2, user7]
    nota.aprobadores = [user3, user4]
    nota.comentadores = [user5, user6]
    nota.estados_aprobacion = {user1.user_id: True, user2.user_id: True, user7.user_id: True, user3.user_id: True, user4.user_id: True}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "4"
    nota.nombre = "Obras Hidraulicas"
    nota.redactores = [user3, user4]
    nota.aprobadores = [user5, user6, user7]
    nota.comentadores = [user1, user2]
    nota.estados_aprobacion = {user3.user_id: True, user4.user_id: False, user5.user_id: True, user6.user_id: False, user7.user_id: False}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "5"
    nota.nombre = "Gestion operacional"
    nota.redactores = [user5, user6]
    nota.aprobadores = [user1, user2]
    nota.comentadores = [user3, user4, user7]
    nota.estados_aprobacion = {user5.user_id: False, user6.user_id: False, user1.user_id: False, user2.user_id: True}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "6"
    nota.nombre = "Proyeccion anual"
    nota.redactores = [user1, user2, user7]
    nota.aprobadores = [user3, user4]
    nota.comentadores = [user5, user6]
    nota.estados_aprobacion = {user1.user_id: True, user2.user_id: True, user7.user_id: True, user3.user_id: True, user4.user_id: True}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "6.1"
    nota.nombre = "Contabilidad del trimestre"
    nota.redactores = [user3, user4]
    nota.aprobadores = [user5, user6, user7]
    nota.comentadores = [user1, user2]
    nota.estados_aprobacion = {user3.user_id: True, user4.user_id: False, user5.user_id: True, user6.user_id: False, user7.user_id: False}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "6.2"
    nota.nombre = "Casos legales"
    nota.redactores = [user5, user6]
    nota.aprobadores = [user1, user2]
    nota.comentadores = [user3, user4, user7]
    nota.estados_aprobacion = {user5.user_id: False, user6.user_id: False, user1.user_id: False, user2.user_id: True}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "7"
    nota.nombre = "Gestiones"
    nota.redactores = [user1, user2, user7]
    nota.aprobadores = [user3, user4]
    nota.comentadores = [user5, user6]
    nota.estados_aprobacion = {user1.user_id: True, user2.user_id: True, user7.user_id: True, user3.user_id: True, user4.user_id: True}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "8"
    nota.nombre = "Excavaciones"
    nota.redactores = [user3, user4]
    nota.aprobadores = [user5, user6, user7]
    nota.comentadores = [user1, user2]
    nota.estados_aprobacion = {user3.user_id: True, user4.user_id: False, user5.user_id: True, user6.user_id: False, user7.user_id: False}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "9"
    nota.nombre = "Relaciones internacionales"
    nota.redactores = [user5, user6]
    nota.aprobadores = [user1, user2]
    nota.comentadores = [user3, user4, user7]
    nota.estados_aprobacion = {user5.user_id: False, user6.user_id: False, user1.user_id: False, user2.user_id: True}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "10"
    nota.nombre = "Cambios"
    nota.redactores = [user1, user2, user7]
    nota.aprobadores = [user3, user4]
    nota.comentadores = [user5, user6]
    nota.estados_aprobacion = {user1.user_id: True, user2.user_id: True, user7.user_id: True, user3.user_id: True, user4.user_id: True}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "11"
    nota.nombre = "Riesgo de operaciones"
    nota.redactores = [user3, user4]
    nota.aprobadores = [user5, user6, user7]
    nota.comentadores = [user1, user2]
    nota.estados_aprobacion = {user3.user_id: True, user4.user_id: False, user5.user_id: True, user6.user_id: False, user7.user_id: False}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "11.1"
    nota.nombre = "Alcance"
    nota.redactores = [user5, user6]
    nota.aprobadores = [user1, user2]
    nota.comentadores = [user3, user4, user7]
    nota.estados_aprobacion = {user5.user_id: False, user6.user_id: False, user1.user_id: False, user2.user_id: True}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "12"
    nota.nombre = "Objetos"
    nota.redactores = [user1, user2, user7]
    nota.aprobadores = [user3, user4]
    nota.comentadores = [user5, user6]
    nota.estados_aprobacion = {user1.user_id: True, user2.user_id: True, user7.user_id: True, user3.user_id: True, user4.user_id: True}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "13"
    nota.nombre = "Finanzas"
    nota.redactores = [user3, user4]
    nota.aprobadores = [user5, user6, user7]
    nota.comentadores = [user1, user2]
    nota.estados_aprobacion = {user3.user_id: True, user4.user_id: False, user5.user_id: True, user6.user_id: False, user7.user_id: False}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    nota = mdl.Nota()
    nota.num = "14"
    nota.nombre = "Metas"
    nota.redactores = [user5, user6]
    nota.aprobadores = [user1, user2]
    nota.comentadores = [user3, user4, user7]
    nota.estados_aprobacion = {user5.user_id: False, user6.user_id: False, user1.user_id: False, user2.user_id: True}
    nota.versiones = []
    nota.comentarios = []
    nota.save()

    return render_template(
        'main.html',
        title='Todo Ok',
        year=datetime.now().year
    )

@app.route('/headers') # TODO: Erase
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
    if utl.running_localhost(request):
        r = requests.get('https://{}/.auth/me'.format(app.config['APP_URL']), cookies={utl.AZURE_COOKIE_NAME:app.config['COOKIE_VALUE']})
        if r.content:
            body = r.json()
            return jsonify(utl.parse_auth_claims(body[0]['user_claims']))
        else:
            return make_response()
    
    access_token = request.headers.get(utl.ACCESS_TOKEN_HEADER)
    if not access_token: # Logout required
        return make_response() #Empty response

    r = requests.get('https://{}/.auth/me'.format(app.config['APP_URL']), headers={'Authorization':'Bearer '+access_token})
    body = r.json()

    if r.status_code == 401 or not body: # Access token expired or error
        return make_response() #Empty response
        
    return jsonify(utl.parse_auth_claims(body[0]['user_claims']))

@app.route('/approval', methods=['POST'])
def approval():
    nota = mdl.Nota.objects.get(num=request.form['nota'])
    if nota.estados_aprobacion[session['user_id']]:
        nota.estados_aprobacion[session['user_id']] = False
        nota.save()
        return jsonify(aprobado=False, msg='Se ha desaprobado la Nota', tipo='success')
    else:
        nota.estados_aprobacion[session['user_id']] = True
        nota.save()
        return jsonify(aprobado=True, msg='Se ha aprobado la Nota', tipo='success')

@app.route('/comment', methods=['POST'])
def comment():
    nota = mdl.Nota.objects.get(num=request.form['nota'])
    version = nota.versiones[-1]
    contenido = request.form['comment']
    redactor = mdl.Usuario.objects.get(user_id=session['user_id'])
    nombre = 'C_' + str(len(version.comentarios) + 1)
    nombre_creacion = "{0}_{1}".format(redactor.iniciales, datetime.now().strftime('%m_%d'))

    comentario = mdl.Comentario()
    comentario.contenido = contenido
    comentario.redactor = redactor
    comentario.nombre = nombre
    comentario.nombre_creacion = nombre_creacion
    comentario.save()
    version.comentarios.append(comentario)
    for aprobador in nota.estados_aprobacion.keys():
        nota.estados_aprobacion[aprobador] = False
    nota.save()
    version.save()
    return jsonify(msg='Se ha guardado el comentario', tipo='success', 
    nombre=nombre, 
    info=nombre_creacion, 
    contenido=contenido)

@app.route('/download_version')
def download_version():
    version_id = request.args['version_id']
    version = mdl.Version.objects.get(id=version_id)
    out = BytesIO(version.archivo.read())
    out.seek(0)
    return send_file(out, attachment_filename=version.archivo.filename, as_attachment=True)

@app.route('/report')
def report():
    modo = request.args.get('modo') # compile or compress
    notas = mdl.Nota.objects
    files = [nota.versiones[-1].archivo for nota in notas]

    if modo == 'compile': # TODO: Receive file name
        # Return all Notas compiled into one
        for filnr, _file in enumerate(files):
            stream = BytesIO(_file.read())
            if filnr == 0:
                merged_document = Document(stream)
                merged_document.add_page_break()
            else:
                sub_doc = Document(stream)

                # Don't add a page break if you've reached the last file.
                if filnr < len(files)-1:
                    sub_doc.add_page_break()

                merged_document.element.body.extend(sub_doc.element.body)
            stream.close()
            
        out = BytesIO()
        merged_document.save(out)
        out.seek(0)
        return send_file(out, attachment_filename="Compilado trimestral.docx", as_attachment=True)

    elif modo == 'compress': # TODO: Receive file name
        # Return all Notas in a .zip file
        out = BytesIO()
        with zipfile.ZipFile(out, 'w') as zf:
            for _file in files:
                info = zipfile.ZipInfo(_file.filename)
                info.date_time = _file.upload_date.timetuple() # Should be download date or upload date??
                # info.date_time = datetime.now().timetuple()
                info.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(info, _file.read())
                
        out.seek(0)
        return send_file(out, attachment_filename='Notas.zip', as_attachment=True)

    return make_response() # Empty response in any other case
