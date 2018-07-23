from sqmwebapp import app

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