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
        session['user'] = user.user_id


# @app.before_request
# def get_authorization():
#     if request.endpoint == 'logout':
#         return
#     print('before request')
#     if not (session.get('login_token') or session.get('state')):
#         print(1)
#         # Generate the guid to only accept initiated logins
#         guid = uuid.uuid4()
#         session['state'] = guid
#         return utl.microsoft.authorize(callback=url_for('authorized', _external=True), state=guid)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('https://{}/.auth/logout'.format(app.config['APP_URL']))

@app.route('/login')
def login():
    if request.args.get("code"):
        session['auth_code'] = request.args.get("code")
    return redirect(url_for('home'))

# @app.route('/login/authorized')
# def authorized():
#     response = utl.microsoft.authorized_response()

#     if response is None:
#         raise Exception( "Access Denied: Reason=%s\nError=%s" % (
#             response.get('error'), 
#             request.get('error_description')
#             )
#         )
        
#     if str(session['state']) != str(request.args['state']):
#         raise Exception('State has been messed with, end authentication')
         
#     session['login_token'] = (response['access_token'], '')
#     return redirect(url_for('home')) 

# @app.route('/me', methods=['POST'])
# def me():
#     def create_oauth_getter(key):
#         def getter():
#             return session.get(key)
#         return getter
#     utl.microsoft.tokengetter(create_oauth_getter('login_token'))
#     me = utl.microsoft.get('me')
    
#     return jsonify(me.data)


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
        version = mdl.Nota.objects(nun=num).versiones[-1] # Query the newest
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
@app.route('/me') # TODO: remove decorator and move to utils
def me():
    """For testing purposes"""
    auth_cookie = request.cookies.get(utl.AZURE_COOKIE_NAME)

    if utl.running_localhost(request):
        r = requests.get('https://{}/.auth/me'.format(app.config['APP_URL']), cookies={utl.AZURE_COOKIE_NAME:utl.COOKIE_VALUE})
        body = r.json()
        return jsonify(utl.parse_auth_claims(body[0]['user_claims']))

    if not auth_cookie: # Logout required
        return make_response() #Empty response

    r = requests.get('https://{}/.auth/me'.format(app.config['APP_URL']), cookies={utl.AZURE_COOKIE_NAME:auth_cookie})
    body = r.json()

    if r.status_code == 401 or not body: # Access token expired or error
        return make_response() #Empty response
        
    return jsonify(utl.parse_auth_claims(body[0]['user_claims']))


@app.route('/headers')
def headers():
    print(request.cookies)
    """For testing purposes"""
    return render_template(
            'test.html',
            message=request.headers
        )

@app.route('/test')
def test():
    """For testing purposes"""
    auth_cookie = request.cookies.get(utl.AZURE_COOKIE_NAME)
    return render_template(
            'test.html',
            message=auth_cookie
        )

@app.route('/test2')
def test2():
    """For testing purposes"""
    auth_cookie = request.headers.get('x-ms-token-aad-access-token')
    return render_template(
            'test.html',
            message=auth_cookie
        )

@app.route('/me2') # TODO: remove decorator and move to utils
def me2():
    """For testing purposes"""
    auth = request.headers.get('x-ms-token-aad-access-token')

    if utl.running_localhost(request):
        r = requests.get('https://{}/.auth/me'.format(app.config['APP_URL']), headers={'Authorization':'Bearer '+auth})
        body = r.json()
        return jsonify(utl.parse_auth_claims(body[0]['user_claims']))

    if not auth: # Logout required
        return make_response() #Empty response

    r = requests.get('https://{}/.auth/me'.format(app.config['APP_URL']), cookies={utl.AZURE_COOKIE_NAME:auth_cookie})
    body = r.json()

    if r.status_code == 401 or not body: # Access token expired or error
        return make_response() #Empty response
        
    return jsonify(utl.parse_auth_claims(body[0]['user_claims']))

# @app.route('/test')
# def test():
#     """For testing purposes"""

#     tenant_id = app.config['TENANT_ID']
#     application_id = app.config['CLIENT_ID']
#     application_secret = app.config['CLIENT_SECRET']

#     data = {'client_id':application_id,
#         'grant_type':'client_credentials',
#         'resource':application_id,
#         'client_assertion':'8N/+5dG73G8LM04aIOX0wOWefcYYah70zPKBguy6R0PsitZ1QIOh6rwOoyQaqkHnZHQKanaqFsYEGPRLqnIQldON/OhHwIYPZNfv3zOLCYH110pSk8Xx2b6QQx20XGb30G/M16k82Lx5/q+q+5AblcIuuCCIjld7di4X+9Inh/n5F7loJ1x6iA+1sdLmhYtbGqrSw10urmopo/c4qnEBEfHieDvHEEtOTZoMOJRxHBmiOk7B11bHOX3XayHxoo+/Z/SnwJegZYTXrEIAhb9MukSQlGBzktVrJnJh/OSKAtClhuhh83wd3vNoV1HdNNeIB++7ucbJGF6pKCXDoCelAeNpYCzPxqPTR8T1R2afVdX0QQoShIQe6py3T0HlKeQTX3CoLMEVperJG7QaQWG1VeOhuQDC9Me2ympaNzEnDrXhnqNYQpJjFwAvK5+vMwuJurdo37ObCFrU5zu2k+dYIzfmJryujwMR86UeJbYNUCII+/uMBAAlKoxChwOyaMaLp77Pb5KzFGvJPacg3lAG6fyJHSGzhlhb5OKfzPL3jMC/cG8NUs4clOuMSEkQlC5vrGDnjFrnt95ucJpltcKbFjupfF97W3k63ZPrVZs508ajrX+/xl24aXzF/j3UOTvE19ich9FgrigqsdM2Fii4oqXW7ET8XR5yIMTRekLPnfO34z8MSuJumO16ZggA4ppcjmjblD/5I8+rD0c723e1IK7N1NZgQFGP7JtRDNxZZ2UvfbR4wKsEtWg3lapbz9XsunwvOkx2xXajQASBAwy4yjnSJkqj4o4TN/NhyCUKO/IWitsMJcq+qIOuhLPZ3F6pNRq025CCsENQZ+BudH/X6lFynbiIgIL29MtqQ6C'}
#     headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#     # Request new token
#     cookies={"AppServiceAuthSession":'8N/ay2pqABcDH55Bn7mC99V5MgyJrpNX19WeAycAdQRAIMZODtzCPvgSUpwpG94fBUpuflICY0eBxUD43hFPsBOCCGw+5dG7a3G8LM04aIOX0wOWefcYYah70zPKBguy6R0PsitZ1QIOh6rwOoyQaqkHnZHQKanaqFsYEGPRLqnIQldON/OhHwIYPZNfv3zOLCYH110pSk8Xx2b6QQx20XGb30G/M16k82Lx5/q+q+5AblcIuuCCIjld7di4X+9Inh/n5F7loJ1x6iA+1sdLmhYtbGqrSw10urmopo/c4qnEBEfHieDvHEEtOTZoMOJRxHBmiOk7B11bHOX3XayHxoo+/Z/SnwJegZYTXrEIAhb9MukSQlGBzktVrJnJh/OSKAtClhuhh83wd3vNoV1HdNNeIB++7ucbJGF6pKCXDoCelAeNpYCzPxqPTR8T1R2afVdX0QQoShIQe6py3T0HlKeQTX3CoLMEVperJG7QaQWG1VeOhuQDC9Me2ympaNzEnDrXhnqNYQpJjFwAvK5+vMwuJurdo37ObCFrU5zu2k+dYIzfmJryujwMR86UeJbYNUCII+/uMBAAlKoxChwOyaMaLp77Pb5KzFGvJPacg3lAG6fyJHSGzhlhb5OKfzPL3jMC/cG8NUs4clOuMSEkQlC5vrGDnjFrnt95ucJpltcKbFjupfF97W3k63ZPrVZs508ajrX+/xl24aXzF/j3UOTvE19ich9FgrigqsdM2Fii4oqXW7ET8XR5yIMTRekLPnfO34z8MSuJumO16ZggA4ppcjmjblD/5I8+rD0c723e1IK7N1NZgQFGP7JtRDNxZZ2UvfbR4wKsEtWg3lapbz9XsunwvOkx2xXajQASBAwy4yjnSJkqj4o4TN/NhyCUKO/IWitsMJcq+qIOuhLPZ3F6pNRq025CCsENQZ+BudH/X6lFynbiIgIL29MtqQ6C'}

#     r = requests.post('https://login.microsoftonline.com/{tenant}/oauth2/token'.format(tenant=tenant_id),
#     data=data, headers=headers, cookies=cookies)
#     print(r.content)

#     r = requests.get('https://{}/.auth/me'.format(app.config['APP_URL']), headers={'Authorization':'Bearer '+r.json()['access_token']})
#     print(r.content)

#     return r.content


# @app.route('/adal')
# def adal():
#     """For testing purposes"""
#     import adal

#     #Static / Dont change

#     tenant_id = app.config['TENANT_ID']
#     application_id = app.config['CLIENT_ID']
#     application_secret = app.config['CLIENT_SECRET']

#     authentication_endpoint = 'https://login.microsoftonline.com/'
#     resource = application_id
#     # get an Azure access token using the service principal
#     context = adal.AuthenticationContext(authentication_endpoint + tenant_id)
#     token_response = context.acquire_token_with_client_credentials(resource, application_id, application_secret)
#     access_token = token_response.get('accessToken')
#     r = requests.get('https://{}/.auth/me'.format(app.config['APP_URL']), headers={"Authorization": "Bearer "+access_token})
#     return jsonify(r.json())


# TODO: Tokens en session, probar dictfield(Usuario:Bool), session[user]: user_id

# TODO sprint: Viste notas completa con cargar/descargar veriones. Sitema de aprobaciones. Poder leer y escribir comentarios.