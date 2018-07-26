from sqmwebapp import app, oauth
import sqmwebapp.models as mdl

# microsoft = oauth.remote_app(
# 	'microsoft',
# 	consumer_key=app.config['CLIENT_ID'],
# 	consumer_secret=app.config['CLIENT_SECRET'],
# 	request_token_params={'scope': 'offline_access User.Read'},
# 	base_url='https://graph.microsoft.com/v1.0/',
# 	request_token_url=None,
# 	access_token_method='POST',
# 	access_token_url=str.format('https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token', tenant=app.config['TENANT_ID']),
# 	authorize_url=str.format('https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize', tenant=app.config['TENANT_ID'])
#     )

def valid_extension(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


# For Version document downloading. TODO: validate extension.
def download_file(file):
    from flask import make_response
    r = make_response(file.read())
    r.headers.set('Content-Disposition', 'attachment', filename=file.filename)
    r.headers['Content-Type'] = 'application/octet-stream'
    if valid_extension(file.filename):
        return r
    else:
        return None

def parse_auth_claims(claims):
    identifiers = {
        'nombre':'name',
        'user_id':'http://schemas.microsoft.com/identity/claims/objectidentifier',
        'email':'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn'
    }

    claims = {claim['typ']:claim['val'] for claim in claims}
    return {k:claims[identifiers[k]] for k in identifiers.keys()}

def running_localhost(request):
    return 'localhost' in request.host

def get_user_via_headers(headers):
    """Lazy alternative for get_or_create_user_via_api()

    Arguments:
        headers -- List of general HTTP headers

    Returns:
        Usuario if exists else None
    """

    id_header = 'x_ms_client_principal_id'
    user_id = headers.get(id_header)
    user = mdl.Usuario.objects(user_id=user_id).first()
    return user


def get_or_create_user_via_api(data):
    """Returns user corresponding to the data retrieved from /.auth/me
    
    Arguments:
        data {JSON} -- Returned from the API call and 
                        processed with parse_auth_claims() 
    
    Returns:
        Usuario -- Object from the DB
    """

    user = mdl.Usuario.objects(user_id=data['user_id']).first()
    if user is None: # First login, create Usuario
        newuser = mdl.Usuario(**data)
        newuser.save()
        return newuser
    return user
