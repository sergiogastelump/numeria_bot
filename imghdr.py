import mimetypes

def what(file, h=None):
    """Compatibilidad para Python 3.13 (módulo imghdr eliminado)."""
    mime_type, _ = mimetypes.guess_type(file)
    if mime_type:
        return mime_type.split("/")[-1]
    return None
