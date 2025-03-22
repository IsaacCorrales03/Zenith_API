from flask import Flask, request, jsonify, render_template, flash, redirect
from werkzeug.utils import secure_filename
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
from flask import send_from_directory

load_dotenv()

app = Flask('__main__')
app.secret_key = 'clave_super_secreta'
URL = "https://zenith-api-38ka.onrender.com"
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


def create_link():
    numeros = ''.join(random.choices(string.digits, k=4))
    letras_minusculas = ''.join(random.choices(string.ascii_lowercase, k=4))
    letras_mayusculas = ''.join(random.choices(string.ascii_uppercase, k=4))
    cadena = numeros + letras_mayusculas + letras_minusculas
    lista_caracteres = list(cadena)
    random.shuffle(lista_caracteres)
    link = ''.join(lista_caracteres)
    return link

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

@app.route('/.well-known/assetlinks.json')
def assetlinks():
    links_json = [{
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {
            "namespace": "android_app",
            "package_name": "com.isaac.zenith",
            "sha256_cert_fingerprints": ["D4:A0:81:B8:6A:65:87:D6:07:E4:AF:B2:4E:48:04:51:A7:1B:CF:DB:B9:64:02:3A:58:24:02:68:CC:B6:4C:DC"]
        }
    }]
    return jsonify(links_json)

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
            SELECT c.id, c.nombre, c.duracion, c.img, uc.progreso
            FROM usuario_curso uc
            JOIN cursos c ON uc.curso_id = c.id
            WHERE uc.usuario_id = %s
        """, (id,))
        
        cursos = cur.fetchall()

        # Construir diccionario de cursos con progreso
        user_dict["cursos"] = [
            {
                "id": curso[0],
                "nombre": curso[1],
                "duracion": curso[2],
                "imagen": curso[3],
                "progreso": curso[4]
            }
            for curso in cursos 
        ]

        # Cerrar cursor
        cur.close()
        # Devolver datos del usuario con cursos
        return jsonify(user_dict)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/crear-curso', methods=['GET', 'POST'])
def crear_curso():
    if request.method == 'GET':
        # Si es una solicitud GET, simplemente mostrar el formulario
        return render_template('cursos.html')
    
    elif request.method == 'POST':
        try:
            # Verificar si la carpeta de destino existe, si no, crearla
            upload_folder = 'assets/cursos'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # Obtener datos del formulario
            nombre = request.form['nombre']
            duracion = request.form['duracion']
            
            # Verificar si se envió un archivo
            if 'imagen' not in request.files:
                flash('No se seleccionó ninguna imagen', 'error')
                return redirect(request.url)
            
            imagen = request.files['imagen']
            
            # Si el usuario no selecciona un archivo, el navegador envía un archivo vacío
            if imagen.filename == '':
                flash('No se seleccionó ninguna imagen', 'error')
                return redirect(request.url)
            
            # Si el archivo existe y tiene una extensión permitida
            if imagen:
                # Asegurar un nombre de archivo único
                filename = secure_filename(imagen.filename)
                # Agregar timestamp al nombre para evitar sobreescrituras
                nombre_archivo = f"{int(time.time())}_{filename}"
                # Guardar la imagen en la carpeta designada
                ruta_imagen = os.path.join(upload_folder, nombre_archivo)
                imagen.save(ruta_imagen)
                
                # Guardar la ruta completa relativa en la base de datos
                ruta_bd = f"{URL}/assets/cursos/{nombre_archivo}"
                # Guardar información en la base de datos
                cursor = mysql.connection.cursor()
                sql = "INSERT INTO cursos (nombre, duracion, img) VALUES (%s, %s, %s)"
                cursor.execute(sql, (nombre, duracion, ruta_bd))
                mysql.connection.commit()
                cursor.close()
                
                flash('Curso creado exitosamente', 'success')
                return redirect('/cursos')  # Redirigir a la lista de cursos
            
        except Exception as e:
            flash(f'Error al crear el curso: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('cursos.html')


@app.route('/cursos')
def listar_cursos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM cursos")
    cursos = cursor.fetchall()
    cursor.close()
    
    # Convertir resultados a lista de diccionarios para facilitar su uso en la plantilla
    cursos_list = []
    for curso in cursos:
        cursos_list.append({
            'id': curso[0],
            'nombre': curso[1],
            'duracion': curso[2],
            'imagen': curso[3]
        })
    
    return jsonify(cursos_list)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assets/cursos/<filename>')
def serve_course_image(filename):
    return send_from_directory('assets/cursos', filename)

@app.route('/enroll/<int:user_id>/<int:curso_id>', methods=['POST'])
def enroll(user_id, curso_id):
    try:
        # Crear cursor
        cur = mysql.connection.cursor()
        
        # Verificar si el usuario existe
        cur.execute('SELECT id FROM usuarios WHERE id = %s', (user_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        # Verificar si el curso existe
        cur.execute('SELECT id FROM cursos WHERE id = %s', (curso_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({"error": "Curso no encontrado"}), 404
            
        # Verificar si ya está inscrito
        cur.execute('SELECT * FROM usuario_curso WHERE usuario_id = %s AND curso_id = %s', 
                   (user_id, curso_id))
        if cur.fetchone():
            cur.close()
            return jsonify({"message": "Usuario ya inscrito en este curso"}), 409
        
        # Insertar en la tabla usuario_curso con progreso inicial 0
        cur.execute('INSERT INTO usuario_curso (usuario_id, curso_id, progreso) VALUES (%s, %s, %s)', 
                   (user_id, curso_id, 0))
        
        # Confirmar la transacción
        mysql.connection.commit()
        
        # Cerrar cursor
        cur.close()
        
        return jsonify({
            "success": True,
            "message": "Usuario inscrito correctamente",
            "usuario_id": user_id,
            "curso_id": curso_id,
            "progreso": 0
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/unsubscribe/<int:user_id>/<int:curso_id>', methods=['DELETE'])
def unsubscribe(user_id, curso_id):
    try:
        # Crear cursor
        cur = mysql.connection.cursor()
        
        # Verificar si el usuario existe
        cur.execute('SELECT id FROM usuarios WHERE id = %s', (user_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        # Verificar si el curso existe
        cur.execute('SELECT id FROM cursos WHERE id = %s', (curso_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({"error": "Curso no encontrado"}), 404
            
        # Verificar si está inscrito
        cur.execute('SELECT * FROM usuario_curso WHERE usuario_id = %s AND curso_id = %s', 
                   (user_id, curso_id))
        if not cur.fetchone():
            cur.close()
            return jsonify({"error": "El usuario no está inscrito en este curso"}), 404
        
        # Eliminar el registro de la tabla usuario_curso
        cur.execute('DELETE FROM usuario_curso WHERE usuario_id = %s AND curso_id = %s', 
                   (user_id, curso_id))
        
        # Confirmar la transacción
        mysql.connection.commit()
        
        # Cerrar cursor
        cur.close()
        
        return jsonify({
            "success": True,
            "message": "Usuario dado de baja correctamente",
            "usuario_id": user_id,
            "curso_id": curso_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/create_group', methods=['POST'])
def create_group():
    name = request.form['name']
    public = request.form['public']
    admin = request.form['admin']
    
    cursor = mysql.connection.cursor()
    

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
        try:
            responce = requests.get(URL, timeout=5)
            print(responce.content[0:10])
            print("BOT REQUEST URL")
        except Exception as e:
            print(f"Error en petición periódica: {str(e)}")
        time.sleep(30)

bot = False
# Iniciar el subproceso
def iniciar_subproceso():
    print("Bot iniciado")
    global bot
    if not bot:
        bot = True
        t = threading.Thread(target=peticion_periodica)
        t.daemon = True  # Asegura que el hilo termine cuando el programa termine
        t.start()

if __name__ == '__main__':
    iniciar_subproceso()
    app.run(host='0.0.0.0', port=8080, debug=True)