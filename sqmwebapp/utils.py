from sqmwebapp import app, oauth

microsoft = oauth.remote_app(
	'microsoft',
	consumer_key=app.config['CLIENT_ID'],
	consumer_secret=app.config['CLIENT_SECRET'],
	request_token_params={'scope': 'offline_access User.Read'},
	base_url='https://graph.microsoft.com/v1.0/',
	request_token_url=None,
	access_token_method='POST',
	access_token_url=str.format('https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token', tenant=app.config['TENANT_ID']),
	authorize_url=str.format('https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize', tenant=app.config['TENANT_ID'])
    )

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
