import secrets
import string
import urllib.parse
import base64
import bcrypt
def generate_group_link():
    caracteres = string.ascii_letters + string.digits  # Letras mayúsculas, minúsculas y números
    link = ''.join(secrets.choice(caracteres) for _ in range(12))  # Genera una cadena de 12 caracteres aleatorios
    return link

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # Encode both the plain password and the stored hashed password
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False
def generate_api_key(length=32):
    # Generar bytes aleatorios
    random_bytes = secrets.token_bytes(length)
    
    # Codificar a base64 y eliminar caracteres problemáticos
    token = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
    
    # Añadir prefijo para identificación
    return token

class PasswordManager:
    @staticmethod
    def hash_password(password: str) -> str:
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            # Convert both passwords to bytes and check
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            print(f"Password verification error: {e}")
            return False
