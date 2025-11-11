# --- Falso módulo imghdr (compatibilidad Python 3.13+) ---
import mimetypes

def what(file, h=None):
    """Sustituye la función original imghdr.what eliminada en Python 3.13"""
    mime_type, _ = mimetypes.guess_type(file)
    if mime_type:
        return mime_type.split("/")[-1]
    return None
