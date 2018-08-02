from sqmwebapp import app
import sqmwebapp.models as mdl

AZURE_COOKIE_NAME = 'AppServiceAuthSession' # Name of azure session cookie
ACCESS_TOKEN_HEADER = 'x-ms-token-aad-access-token'

def valid_extension(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def parse_auth_claims(claims):
    identifiers = {
        'nombre':'name',
        'user_id':'http://schemas.microsoft.com/identity/claims/objectidentifier',
        'email':'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name'
    }

    claims = {claim['typ']:claim['val'] for claim in claims}
    return {k:claims.get(identifiers[k]) for k in identifiers.keys()}

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
    if user_id:
        user = mdl.Usuario.objects(user_id=user_id).first()
        return user
    return None


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
