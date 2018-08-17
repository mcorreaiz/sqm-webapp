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
from mongoengine.queryset.visitor import Q

import sqmwebapp.models as mdl
import sqmwebapp.utils as utl
from sqmwebapp import app

@app.before_request
def register():
    if request.url == 'https://{}/.auth/logout'.format(app.config['APP_URL']):
        return
    if 'user' not in session: # Not registered with DB or session expired
        # Lazy auth
        user = utl.get_user_via_headers(request.headers)
        if user is None: # New user, or header failed somehow
            data = me()
            if not data.get_json(): # Empty body means the API requires new auth
                return redirect('https://{}/.auth/logout'.format(app.config['APP_URL']))
            user = utl.get_or_create_user_via_api(data.get_json())
        session['user'] = user.nombre
        session['user_id'] = user.user_id
        session['admin'] = user.admin
        session['trimestre_id'] = str(mdl.Trimestre.objects.order_by("-fecha").first().id)
        session['is_last_trimestre'] = True

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    return redirect('https://{}/.auth/logout'.format(app.config['APP_URL']))

@app.route('/')
def notas():
    """Renders the overview of the Notas state."""
    usuario = mdl.Usuario.objects.get(user_id=session['user_id'])
    trimestres = mdl.Trimestre.objects
    trimestre = trimestres.get(id=session.get('trimestre_id'))
    notas_trim = trimestre.notas
    redacciones = set(mdl.Nota.objects(redactores__in=[usuario]))
    aprobaciones = set(mdl.Nota.objects(aprobadores__in=[usuario]))
    comentarios = set(mdl.Nota.objects(comentadores__in=[usuario]))
    return render_template(
        'notas.html',
        year = datetime.now().year,
        user = usuario,
        users = mdl.Usuario.objects,
        trimestre = trimestre,
        trimestres = trimestres,
        redacciones = [nota for nota in notas_trim if nota in redacciones],
        aprobaciones = [nota for nota in notas_trim if nota in aprobaciones],
        comentarios = [nota for nota in notas_trim if nota in comentarios]
    )

@app.route('/notas/<num>', methods=['GET', 'POST'])
def nota_panel(num, trimestre_id=None):
    """Renders the description of a Nota object."""
    num = unquote(num)
    trimestre = mdl.Trimestre.objects.get(id=session.get('trimestre_id'))
    nota = next((x for x in trimestre.notas if x.num == num), None)

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Ningun archivo seleccionado', 'error')
            return redirect(request.url)

        file = request.files['file']

        # If user submits an empty form
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
        year = datetime.now().year,
        nota = nota,
        trimestre = trimestre,
        user = mdl.Usuario.objects.get(user_id=session['user_id']),
        version = nota.versiones[-1] if nota.versiones else mdl.Version(nombre_creacion="No hay versiones", nombre="")
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
    
    auth_cookie = request.cookies.get(utl.AZURE_COOKIE_NAME)
    if not auth_cookie: # Logout required
        return make_response() #Empty response

    r = requests.get('https://{}/.auth/me'.format(app.config['APP_URL']), cookies={utl.AZURE_COOKIE_NAME:auth_cookie})
    body = r.json()

    if r.status_code == 401 or not body: # Access token expired or error
        return make_response() #Empty response
        
    return jsonify(utl.parse_auth_claims(body[0]['user_claims']))

@app.route('/approval', methods=['POST'])
def approval():
    trimestre = mdl.Trimestre.objects.get(id=session.get('trimestre_id'))
    nota = next((x for x in trimestre.notas if x.num == request.form['nota']), None)
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
    trimestre = mdl.Trimestre.objects.get(id=session.get('trimestre_id'))
    nota = next((x for x in trimestre.notas if x.num == request.form['nota']), None)
    version = nota.versiones[-1]
    contenido = request.form['comment']
    redactor = mdl.Usuario.objects.get(user_id=session['user_id'])
    nombre = 'C_' + str(len(version.comentarios))
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

@app.route('/admin')
def admin():
    trimestre = mdl.Trimestre.objects.order_by("-fecha").first()
    notas_aprobadas = 0
    notas_cerradas = 0
    for nota in trimestre.notas:
        if nota.full_aprobado:
            notas_aprobadas += 1
        if nota.cerrada:
            notas_cerradas += 1
    
    admins = mdl.Usuario.objects(admin=True)
    admins2 = mdl.Usuario.objects(Q(admin=True) & Q(user_id__ne=session['user_id']))
    
    return render_template(
        'admin.html',
        trimestre = trimestre,
        notas_aprobadas = notas_aprobadas,
        notas_cerradas = notas_cerradas,
        total = len(trimestre.notas),
        admins = admins,
        admins2 = admins2,
        not_admins = mdl.Usuario.objects(admin=False)
    )

@app.route('/cierres', methods=['POST'])
def cierres():
    trimestre = mdl.Trimestre.objects.order_by("-fecha").first()
    user = mdl.Usuario.objects.get(user_id=session['user_id'])

    # Acciones para cerrar el trimestre
    if trimestre.activo:
        trimestre.activo = False
        trimestre.save()
        for nota in trimestre.notas:
            nota.cerrada = True
            nota.save()
        notas_cerradas = '{} / {}'.format(len(trimestre.notas), len(trimestre.notas)) 
        return jsonify(cerrado=True, msg='Se ha cerrado el trimestre', tipo='success', notas_cerradas=notas_cerradas)

    else:
        # Creamos el nuevo trimestre
        new_trimestre = mdl.Trimestre()
        new_trimestre.numero = (trimestre.numero % 4) + 1
        new_trimestre.notas = []
        # Cargamos el trimestre con las notas del trimestre pasado, usando la última versión como base
        for nota in trimestre.notas:
            new_nota = mdl.Nota()
            new_nota.num = nota.num
            new_nota.nombre = nota.nombre
            new_nota.redactores = nota.redactores
            new_nota.aprobadores = nota.aprobadores
            new_nota.comentadores = nota.comentadores
            new_nota.estados_aprobacion = nota.estados_aprobacion
            # Nadie ha aprobado la nueva nota
            for aprobacion in new_nota.estados_aprobacion.keys():
                new_nota.estados_aprobacion[aprobacion] = False
            # Creamos una nueva versión que será la base de new_nota
            version_base = mdl.Version()
            if len(nota.versiones):
                ultima_version = nota.versiones[-1]
                version_base.archivo = ultima_version.archivo
            version_base.redactor = user
            version_base.nombre = "R_b"
            version_base.nombre_creacion = "{}_{}".format(user.iniciales, version_base.fecha.strftime('%m_%d'))
            # Versión base viene con comentario: Carga inicial
            comentario_base = mdl.Comentario()
            comentario_base.contenido = "Carga inicial"
            comentario_base.redactor = user
            comentario_base.nombre = "C_0"
            comentario_base.nombre_creacion = "{}_{}".format(user.iniciales, comentario_base.fecha.strftime('%m_%d'))
            comentario_base.save()
            version_base.comentarios = [comentario_base]
            # Guardamos los objetos nuevos
            version_base.save()
            new_nota.versiones = [version_base]
            new_nota.save()
            new_trimestre.notas.append(new_nota)
        new_trimestre.save()
        session['trimestre_id'] = str(new_trimestre.id)
        notas_cerradas = '0 / {}'.format(len(new_trimestre.notas))
        return jsonify(cerrado=False, msg='Se ha creado un nuevo trimestre', tipo='success', notas_cerradas=notas_cerradas, nombre_trimestre=new_trimestre.nombre)


@app.route('/add_admin', methods=['POST'])
def add_admin():
    if request.form['user'] == 'Ninguno':
        return jsonify(msg='Debe seleccionar a un Usuario', tipo='error')
    usuario = mdl.Usuario.objects.get(nombre=request.form['user'])
    usuario.admin = True
    usuario.save() 
    return jsonify(msg='{} es Administrador'.format(request.form['user']), tipo='success')

@app.route('/del_admin', methods=['POST'])
def del_admin():
    if request.form['user'] == 'Ninguno':
        return jsonify(msg='Debe seleccionar a un Usuario', tipo='error')
    usuario = mdl.Usuario.objects.get(nombre=request.form['user'])
    usuario.admin = False
    usuario.save() 
    return jsonify(msg='{} ya no es Administrador'.format(request.form['user']), tipo='success')

@app.route('/add_nota', methods=['POST'])
def add_nota():
    if request.form['numero'] == '' or request.form['descripcion'] == '':
        return jsonify(msg='Debe ingresar el numero y la descripción de la nota', tipo='error')

    trimestre = mdl.Trimestre.objects.order_by("-fecha").first()

    redactores = request.form.getlist('redactores[]')
    aprobadores = request.form.getlist('aprobadores[]')
    comentadores = request.form.getlist('comentadores[]')

    new_nota = mdl.Nota()
    new_nota.num = request.form['numero']
    new_nota.nombre = request.form['descripcion']
    new_nota.redactores = []
    new_nota.aprobadores = []
    new_nota.comentadores = []
    new_nota.estados_aprobacion = {}
    new_nota.versiones = []

    for user in redactores:
        usuario = mdl.Usuario.objects.get(nombre=user)
        new_nota.redactores.append(usuario)
        new_nota.estados_aprobacion[usuario.user_id] = False
    
    for user in aprobadores:
        usuario = mdl.Usuario.objects.get(nombre=user)
        new_nota.aprobadores.append(usuario)
        new_nota.estados_aprobacion[usuario.user_id] = False

    for user in comentadores:
        usuario = mdl.Usuario.objects.get(nombre=user)
        new_nota.comentadores.append(usuario)

    new_nota.save()
    trimestre.notas.append(new_nota)
    trimestre.save()

    return jsonify(msg='Se ha agregado la nota', tipo='success')

@app.route('/add_trimestre')
def add_trimestre():
    trimestre = mdl.Trimestre()
    trimestre.notas = mdl.Nota.objects()
    trimestre.numero = 3
    trimestre.save()
    return redirect(url_for('notas'))

@app.route('/report')
def report():
    modo = request.args.get('modo') # compile or compress
    trimestre = mdl.Trimestre.objects.get(id=session.get('trimestre_id'))
    nota = trimestre.notas
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

@app.route('/change_trimestre')
@app.route('/change_trimestre/<trimestre_id>')
def change_trimestre(trimestre_id=None):
    if trimestre_id:
        session['trimestre_id'] = trimestre_id
        if trimestre_id == mdl.Trimestre.objects.order_by("-fecha").first().id:
            session['is_last_trimestre'] = True
        else:
            session['is_last_trimestre'] = False
    else: # Go to last Trimestre
        session['trimestre_id'] = str(mdl.Trimestre.objects.order_by("-fecha").first().id)
        session['is_last_trimestre'] = True

    return redirect(url_for('notas'))
