"""
Routes and views for the flask application.
"""

import uuid
from datetime import datetime

import requests
from flask import (flash, jsonify, make_response, redirect, render_template,
                   request, session, url_for)
from werkzeug.utils import secure_filename

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
            if not data:
                return redirect('https://{}/.auth/logout'.format(app.config['APP_URL']))
            user = utl.get_or_create_user_via_api(data.get_json())
        session['user'] = user.nombre


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


# @app.route('/logout')
# def logout():
#     session.pop('login_token', None)
#     session.pop('state', None)
#     return redirect(url_for('home'))
#     # return redirect('/.auth/logout?post_logout_redirect_uri=/home') 

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
        version = mdl.Version.objects.order_by('-fecha').first() # Query the newest
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

@app.route('/me') # TODO: remove decorator and move to utils
def me():
    """For testing purposes"""
    # import adal

    # #Static / Dont change
    # authentication_endpoint = 'https://login.microsoftonline.com/'
    # resource = 'https://graph.microsoft.com'

    tenant_id = app.config['TENANT_ID']
    application_id = app.config['CLIENT_ID']
    application_secret = app.config['CLIENT_SECRET']

    # ## get an Azure access token using the service principal
    # context = adal.AuthenticationContext(authentication_endpoint + tenant_id)
    # token_response = context.acquire_token_with_client_credentials(resource, application_id, application_secret)
    # access_token = token_response.get('accessToken')

    r = requests.get('https://{}/.auth/me'.format(app.config['APP_URL']), headers={"Authorization": "Bearer "+app.config['AAD_TOKEN']})
    body = r.json()

    if r.status_code == 401: # Access token expired
        data = {'client_id':application_id,
        'refresh_token':app.config['AAD_REFRESH_TOKEN'],
        'grant_type':'refresh_token',
        'resource':application_id,
        'client_secret':application_secret}

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        # Request new token
        r = requests.post('https://login.microsoftonline.com/{tenant}/oauth2/token'.format(tenant=tenant_id),
        data=data, headers=headers)

        app.config['AAD_TOKEN'] = r.json()['access_token']
        app.config['AAD_REFRESH_TOKEN'] = r.json()['refresh_token']

        r = requests.get('https://{}/.auth/me'.format(app.config['APP_URL']), headers={"Authorization": "Bearer "+app.config['AAD_TOKEN']})
        body = r.json()

    if not body: # Empty body means the API requires new auth
        return None
        
    return jsonify(utl.parse_auth_claims(body[0]['user_claims']))


@app.route('/headers')
def headers():
    """For testing purposes"""
    return render_template(
            'test.html',
            message=request.headers
        )
