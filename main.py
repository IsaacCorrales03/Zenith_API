from flask import Flask, request, jsonify, render_template, flash, redirect
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
from flask_cors import CORS
import os
import bcrypt
import json
from dotenv import load_dotenv
import urllib.parse
from flask import send_from_directory
from server_strings import *
from criptografic import generate_api_key, generate_group_link
load_dotenv()

app = Flask('__main__')

# Configuración clave de sesión (debe ser fija para evitar que se pierda)
app.secret_key = os.getenv('secret_key')
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuración de MySQL
app.config['MYSQL_HOST'] = os.getenv('host')
app.config['MYSQL_USER'] = os.getenv('user')
app.config['MYSQL_PASSWORD'] = os.getenv('password')
app.config['MYSQL_DB'] = os.getenv('db')
app.config['MYSQL_PORT'] = int(os.getenv('port'))

mysql = MySQL(app)



@app.route('/.well-known/assetlinks.json')
def assetlinks():
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
            return jsonify({error: error_not_found_user}), 404

        # Obtener nombres de columnas
        column_names = [desc[0] for desc in cur.description]

        # Construir diccionario del usuario
        user_dict = dict(zip(column_names, user_row))
        user_api_key = urllib.parse.unquote(user_dict.get("hashed_api_key"))

        if user_api_key != api_key:
            cur.close()
            return jsonify({error: error_access_not_authorized}), 401

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
                flash(error_not_image_provided, error)
                return redirect(request.url)
            
            imagen = request.files['imagen']
            
            # Si el usuario no selecciona un archivo, el navegador envía un archivo vacío
            if imagen.filename == '':
                flash(error_not_image_provided, error)
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
                ruta_bd = f"{service_url}/assets/cursos/{nombre_archivo}"
                # Guardar información en la base de datos
                cursor = mysql.connection.cursor()
                sql = "INSERT INTO cursos (nombre, duracion, img) VALUES (%s, %s, %s)"
                cursor.execute(sql, (nombre, duracion, ruta_bd))
                mysql.connection.commit()
                cursor.close()
                
                flash(info_course_created_correctly, success)
                return redirect('/cursos')  # Redirigir a la lista de cursos
            
        except Exception as e:
            flash(f'{error_creating_course}: {str(e)}', error)
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
            return jsonify({error: error_not_found_user}), 404
            
        # Verificar si el curso existe
        cur.execute('SELECT id FROM cursos WHERE id = %s', (curso_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({error: error_not_found_course}), 404
            
        # Verificar si ya está inscrito
        cur.execute('SELECT * FROM usuario_curso WHERE usuario_id = %s AND curso_id = %s', 
                   (user_id, curso_id))
        if cur.fetchone():
            cur.close()
            return jsonify({message: info_user_already_enroll}), 409
        
        # Insertar en la tabla usuario_curso con progreso inicial 0
        cur.execute('INSERT INTO usuario_curso (usuario_id, curso_id, progreso) VALUES (%s, %s, %s)', 
                   (user_id, curso_id, 0))
        
        # Confirmar la transacción
        mysql.connection.commit()
        
        # Cerrar cursor
        cur.close()
        
        return jsonify({
            "success": True,
            "message": info_user_enrolled,
            "usuario_id": user_id,
            "curso_id": curso_id,
            "progreso": 0
        })
        
    except Exception as e:
        return jsonify({error: str(e)}), 500

@app.route('/unsubscribe/<int:user_id>/<int:curso_id>', methods=['DELETE'])
def unsubscribe(user_id, curso_id):
    try:
        # Crear cursor
        cur = mysql.connection.cursor()
        
        # Verificar si el usuario existe
        cur.execute('SELECT id FROM usuarios WHERE id = %s', (user_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({error: error_not_found_user}), 404
            
        # Verificar si el curso existe
        cur.execute('SELECT id FROM cursos WHERE id = %s', (curso_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({error: error_not_found_course}), 404
            
        # Verificar si está inscrito
        cur.execute('SELECT * FROM usuario_curso WHERE usuario_id = %s AND curso_id = %s', 
                   (user_id, curso_id))
        if not cur.fetchone():
            cur.close()
            return jsonify({error: error_user_not_in_course}), 404
        
        # Eliminar el registro de la tabla usuario_curso
        cur.execute('DELETE FROM usuario_curso WHERE usuario_id = %s AND curso_id = %s', 
                   (user_id, curso_id))
        
        # Confirmar la transacción
        mysql.connection.commit()
        
        # Cerrar cursor
        cur.close()
        
        return jsonify({
            "success": True,
            "message": info_user_unsubscribe,
            "usuario_id": user_id,
            "curso_id": curso_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


    

@app.route('/create_user', methods=['POST'])
def create_user():
    try:
        # Obtener datos del request
        data = request.get_json()
        
        # Validar datos requeridos
        if not data or 'nombre' not in data or 'correo' not in data or 'contraseña' not in data:
            return jsonify({nombre: error_credentials_not_provided}), 400
        
        # Extraer datos
        nombre = data.get('nombre')
        correo = data.get('correo')
        contraseña = data.get('contraseña')
        
        # Encriptar la contraseña
        hashed_password = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())

        # Concatenar todo en el orden especificado
        api_key = generate_api_key()
        
        # Crear cursor
        cur = mysql.connection.cursor()
        
        # Verificar si el correo ya existe
        cur.execute('SELECT id FROM usuarios WHERE correo = %s', (correo,))
        if cur.fetchone():
            cur.close()
            return jsonify({error: error_email_already_register}), 409
        
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
            "message": infor_user_created_correctly,
            "user_id": user_id,
            "api_key": api_key  # Opcional: devolver la api_key al usuario
        }), 201
    
    except Exception as e:
        # Si ocurre algún error, hacer rollback
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    

@app.route('/group_data/<int:group_id>')
def group_data(group_id):
    try:
        cursor = mysql.connection.cursor()
        
        # Usar el parámetro group_id en lugar de hardcodear 1
        cursor.execute("SELECT * FROM grupos WHERE id = %s", (group_id,))
        data = cursor.fetchone()
        
        if not data:
            return jsonify({"error": "Grupo no encontrado"}), 404
        
        # Con Flask-MySQLdb, fetchone() devuelve una tupla, no un diccionario
        # Obtener el admin_id del índice 4
        admin_id = data[4]
        
        # Obtener el nombre del admin en una consulta separada
        cursor.execute("SELECT nombre FROM usuarios WHERE id = %s", (admin_id,))
        admin_result = cursor.fetchone()
        
        if not admin_result:
            admin_nombre = "Desconocido"  # Valor por defecto si no se encuentra el admin
        else:
            admin_nombre = admin_result[0]  # El primer elemento de la tupla
        
        # Crear el diccionario de respuesta usando los índices
        data_json = {
            'id': data[0],
            'nombre': data[1],
            'banner': data[2],
            'miembros': data[3],
            'admin': admin_nombre,
            'public': data[5],
            'description': data[6]
        }
        
        mysql.connection.commit()  # Asegurar que se han completado las operaciones
        return jsonify(data_json), 200
    
    except Exception as e:
        # Manejo de errores
        app.logger.error(f"Error al obtener datos del grupo: {str(e)}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500
    
    finally:
        # Cerrar el cursor explícitamente
        if 'cursor' in locals() and cursor:
            cursor.close()


import threading
import time
import requests
def peticion_periodica():
    while True:
        try:
            responce = requests.get(service_url, timeout=5)
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