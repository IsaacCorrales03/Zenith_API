import secrets
import string
import urllib.parse
import base64

def generate_group_link():
    caracteres = string.ascii_letters + string.digits  # Letras mayúsculas, minúsculas y números
    link = ''.join(secrets.choice(caracteres) for _ in range(12))  # Genera una cadena de 12 caracteres aleatorios
    return link

def generate_api_key(length=32):
    # Generar bytes aleatorios
    random_bytes = secrets.token_bytes(length)
    
    # Codificar a base64 y eliminar caracteres problemáticos
    token = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
    
    # Añadir prefijo para identificación
    return token
