"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, make_response, flash, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
import uuid

from sqmwebapp import app
import sqmwebapp.utils as u
import sqmwebapp.models as mdl
import requests

@app.before_request
def get_authorization():
    print('before request')
    if not session.get('login_token') and not session.get('state'):
        print(1)
        # Generate the guid to only accept initiated logins
        guid = uuid.uuid4()
        session['state'] = guid
        return u.microsoft.authorize(callback=url_for('authorized', _external=True), state=guid)
	
@app.route('/logout')
def logout():
    session.pop('login_token', None)
    session.pop('state', None)
    return redirect(url_for('home')) 

@app.route('/login/authorized')
def authorized():
    response = u.microsoft.authorized_response()

    if response is None:
        raise Exception( "Access Denied: Reason=%s\nError=%s" % (
            response.get('error'), 
            request.get('error_description')
            )
        )
        
    if str(session['state']) != str(request.args['state']):
        raise Exception('State has been messed with, end authentication')
         
    session['login_token'] = (response['access_token'], '')
    return redirect(url_for('home')) 

@app.route('/me')
def me():
    def create_oauth_getter(key):
        def getter():
            return session.get(key)
        return getter
    u.microsoft.tokengetter(create_oauth_getter('login_token'))
    me = u.microsoft.get('me')
    
    return jsonify(me.data)


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

@app.route('/adal')
def adal():
    import adal

    #Static / Dont change
    authentication_endpoint = 'https://login.microsoftonline.com/'  #Static
    resource = 'https://graph.microsoft.com'  #Static

    tenant_id = app.config['TENANT_ID']  #AAD->Properties->Directory ID
    application_id = app.config['CLIENT_ID'] #register app in AAD -> app registrations -> new application registration
    application_secret = app.config['CLIENT_SECRET'] #open registered app and create a key with whatever name. when you save, you will get a secret.

    ## get an Azure access token using the service principal
    context = adal.AuthenticationContext(authentication_endpoint + tenant_id)
    token_response = context.acquire_token_with_client_credentials(resource, application_id, application_secret)
    access_token = token_response.get('accessToken')

    r = requests.get('https://graph.microsoft.com/v1.0/$metadata#users/$entity', headers={"Authorization": "Bearer "+access_token})

    """For testing purposes"""
    return render_template(
            'test.html',
            message=r.text
        )
