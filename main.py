from flask import Flask, request, jsonify, render_template
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_cors import CORS
import os
import string
import random
import bcrypt
import json
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

app = Flask('__main__')
app.secret_key = 'clave_super_secreta'

# Configuración clave de sesión (debe ser fija para evitar que se pierda)
app.secret_key = os.getenv('SECRET_KEY', 'clave_secreta_por_defecto')
CORS(app, resources={r"/*": {"origins": "*"}})
# Configuración de MySQL
app.config['MYSQL_HOST'] = os.getenv('host')
app.config['MYSQL_USER'] = os.getenv('user')
app.config['MYSQL_PASSWORD'] = os.getenv('password')
app.config['MYSQL_DB'] = os.getenv('db')
app.config['MYSQL_PORT'] = int(os.getenv('port'))

mysql = MySQL(app)


@app.route('/user/<int:id>/<string:api_key>')
def user_data(id, api_key):
    try:
        # Crear cursor
        cur = mysql.connection.cursor()
        
        # Consulta para obtener datos del usuario
        cur.execute('SELECT * FROM usuarios WHERE id = %s', (id,))
        user_row = cur.fetchone()

        if not user_row:
            cur.close()
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Obtener nombres de columnas
        column_names = [desc[0] for desc in cur.description]

        # Construir diccionario del usuario
        user_dict = dict(zip(column_names, user_row))
        user_api_key = urllib.parse.unquote(user_dict.get("hashed_api_key"))

        if user_api_key != api_key:
            cur.close()
            return jsonify({"error": "ACCESO NO AUTORIZADO"}), 401

        # Convertir cadenas JSON a objetos Python si existen
        for key in ["porcentaje_de_aprendizajes", "preferencias", "retroalimentacion"]:
            if user_dict.get(key):
                user_dict[key] = json.loads(user_dict[key])

        # Consulta para obtener los cursos del usuario
        cur.execute("""
            SELECT c.id, c.nombre, c.duracion, c.img 
            FROM usuario_curso uc
            JOIN cursos c ON uc.curso_id = c.id
            WHERE uc.usuario_id = %s
        """, (id,))
        
        cursos = cur.fetchall()

        # Obtener nombres de columnas de la tabla cursos
        cursos_column_names = [desc[0] for desc in cur.description]

        # Construir diccionario de cursos
        user_dict["cursos"] = [
            {
                "id": curso[0],
                "nombre": curso[1],
                "duracion": curso[2],
                "imagen": curso[3]
            }
            for curso in cursos 
        ]

        # Cerrar cursor
        cur.close()
        print(user_dict)
        # Devolver datos del usuario con cursos
        return jsonify(user_dict)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

def generar_api_key():
    # Generar los grupos de caracteres
    numeros = ''.join(random.choices(string.digits, k=12))
    letras_minusculas = ''.join(random.choices(string.ascii_lowercase, k=12))
    simbolos = ''.join(random.choices('!@#$%^&*()_+-=[]{}|;:,.<>', k=12))
    letras_mayusculas = ''.join(random.choices(string.ascii_uppercase, k=12))
    
    # Combinar todos los caracteres
    todos_los_caracteres = numeros + letras_minusculas + simbolos + letras_mayusculas
    
    # Convertir a lista para poder mezclar
    lista_caracteres = list(todos_los_caracteres)
    
    # Mezclar la lista aleatoriamente
    random.shuffle(lista_caracteres)
    
    # Convertir de nuevo a string
    api_key = ''.join(lista_caracteres)
    
    # Codificar la API Key para ser segura en URLs
    api_key_codificada = urllib.parse.quote(api_key)
    
    return api_key_codificada

@app.route('/create_user', methods=['POST'])
def create_user():
    try:
        # Obtener datos del request
        data = request.get_json()
        
        # Validar datos requeridos
        if not data or 'nombre' not in data or 'correo' not in data or 'contraseña' not in data:
            return jsonify({"error": "Nombre, correo y contraseña son requeridos"}), 400
        
        # Extraer datos
        nombre = data.get('nombre')
        correo = data.get('correo')
        contraseña = data.get('contraseña')
        
        # Encriptar la contraseña
        hashed_password = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())

        # Concatenar todo en el orden especificado
        api_key = generar_api_key()
        
        # Crear cursor
        cur = mysql.connection.cursor()
        
        # Verificar si el correo ya existe
        cur.execute('SELECT id FROM usuarios WHERE correo = %s', (correo,))
        if cur.fetchone():
            cur.close()
            return jsonify({"error": "El correo ya está registrado"}), 409
        
        # Ejecutar la consulta para insertar usuario
        cur.execute(
            'INSERT INTO usuarios (nombre, correo, clave, hashed_api_key) VALUES (%s, %s, %s, %s)',
            (nombre, correo, hashed_password, api_key)
        )
        
        # Obtener el ID del usuario recién insertado
        user_id = cur.lastrowid
        
        # Confirmar la transacción
        mysql.connection.commit()
        
        # Cerrar cursor
        cur.close()
        
        return jsonify({
            "message": "Usuario creado exitosamente",
            "user_id": user_id,
            "api_key": api_key  # Opcional: devolver la api_key al usuario
        }), 201
    
    except Exception as e:
        # Si ocurre algún error, hacer rollback
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    
import threading
import time
import requests
def peticion_periodica():
    while True:
        # Llamar a la función que deseas ejecutar
        requests.get("https://zenith-api-38ka.onrender.com")
        time.sleep(40)

bot = False
# Iniciar el subproceso
def iniciar_subproceso():
    global bot
    if not bot:
        bot = True
        t = threading.Thread(target=peticion_periodica)
        t.daemon = True  # Asegura que el hilo termine cuando el programa termine
        t.start()

app.run(host='0.0.0.0', port=8080)