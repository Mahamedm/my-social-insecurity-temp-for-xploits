import magic
from flask import current_app as app

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def allowed_mime_type(file_stream):
    """Check if the file has an allowed MIME type."""
    file_stream.seek(0)
    mime_type = magic.from_buffer(file_stream.read(1024), mime=True)
    file_stream.seek(0)
    return mime_type in app.config['ALLOWED_MIME_TYPES']