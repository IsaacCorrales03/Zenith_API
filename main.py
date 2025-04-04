from flask import Flask, jsonify, request, render_template,send_from_directory
from flask_cors import CORS
import os
import crud
from werkzeug.utils import secure_filename
from server_strings import *
from bot import Bot

app = Flask('__main__')
app.secret_key = os.getenv('secret_key')
CORS(app, resources={r"/*": {"origins": "*"}})

# Carpetas de archivos
UPLOAD_FOLDER_BASE = "assets"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER_BASE
UPLOAD_FOLDER_CURSOS = os.path.join(UPLOAD_FOLDER_BASE, "cursos")
os.makedirs(UPLOAD_FOLDER_CURSOS, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/usuario', methods=['POST', 'GET'])
def usuarios():
    if request.method == 'GET':
        usuario_id = request.args.get('id', type=int)
        api_key = request.args.get('api_key', type=str)

        if not all([usuario_id, api_key]):
            return jsonify({'error': 'Faltan credenciales'}), 400
        
        try:
            data = crud.obtener_usuario_by_id(id=usuario_id, api_key=api_key)
            return jsonify(data) if data else ('Usuario no encontrado', 404)
        except Exception as e:
            return jsonify({'error': f'Error al obtener usuario: {str(e)}'}), 500
    elif request.method == 'POST':
        data = request.json or {}
        required_fields = {'username', 'email', 'password'}

        if not required_fields.issubset(data):
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        if '@' not in data['email'] or '.' not in data['email']:
            return jsonify({'error': 'Formato de correo inválido'}), 400
        
        try:
            user = crud.crear_usuario(
                nombre=data['username'], 
                correo=data['email'], 
                password=data['password']
            )
            if user == 400:
                return jsonify({'error':'El nombre o correo ya está en uso'})
            if user == 401:
                return jsonify({'error':'El nombre es demasiado largo'})
            return jsonify({'message':'Usuario Creado con éxito','User_ID': user.id, 'Api_Key': user.api_key}), 201
        except Exception as e:
            return jsonify({'error': f'Error al crear usuario: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("correo")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Faltan credenciales"}), 400
    
    resultado = crud.iniciar_sesion(email, password)
    
    if resultado == 401:
        return jsonify({"error": "Credenciales incorrectas"}), 401
    elif resultado == 500:
        return jsonify({"error": "Error interno del servidor"}), 500
    
    return jsonify({
        "mensaje": "Inicio de sesión exitoso",
        "usuario": {
            "id": resultado.id,
            "nombre": resultado.nombre,
            "correo": resultado.correo,
            "api_key": resultado.api_key
        }
    }), 200

@app.route('/cursos', methods=['POST', 'GET', 'PUT', 'DELETE'])
def cursos():
    if request.method == 'GET':
        id_curso = request.args.get('id', type=int)
        if not id_curso:
            return 'No se especifíca un curso', 400
        curso = crud.obtener_curso_by_id(id_curso)
        if not curso:
            return 'No se encontró un curso', 400
        return jsonify(curso)
    elif request.method == 'POST':
        if not request.content_type.startswith('multipart/form-data'):
            return jsonify({"error": "La solicitud debe ser multipart/form-data"}), 400
        
        curso_name = request.form.get('nombre')
        curso_duracion = request.form.get('duracion', type=int)
        curso_imagen = request.files.get('imagen') 
        if not curso_name or not curso_duracion or not curso_imagen:
            return jsonify({"error": "Faltan datos obligatorios"}), 400
        filename = secure_filename(curso_imagen.filename)
        image_path = os.path.join(UPLOAD_FOLDER_CURSOS, filename)
        curso_imagen.save(image_path)
        img_url = f'{service_url}/{image_path}'
        curso = crud.crear_curso(nombre=curso_name, duracion=curso_duracion, url_imagen=img_url)
        return {'Info': 'Created course'}, 200
    elif request.method == 'PUT':
        id_usuario = request.form.get('usuario_id', type=int)
        id_curso = request.form.get('curso_id', type=int)
        if not id_curso or not id_usuario:
            return {'error': 'Faltan datos'}, 400
        resultado = crud.inscribir_usuario_a_curso(id_usuario=id_usuario, id_curso=id_curso)
        if resultado:
            return {'mensaje': 'El usuario se inscribió al curso correctamente'}, 200
        else:
            return {'error': 'El usuario ya está en el curso o ocurrió un error'}, 400
    elif request.method == 'DELETE':
        usuario_id = request.args.get('usuario_id', type=int)
        curso_id = request.args.get('curso_id', type=int)
        if not usuario_id or not curso_id:
            return {'error': 'Faltan datos'}, 400
        resultado = crud.darse_de_baja_de_un_curso(id_usuario)
        if not resultado:
            return {'error', 'Algo salió mal'}, 400
        return {'mensaje': 'El usuario se dio de baja'}

@app.route('/grupos', methods=['POST', 'GET', 'PUT', 'DELETE'])
def grupos():
    if request.method == 'GET':
        id_grupo = request.args.get('id', type=int)
        codigo = request.args.get('codigo', type=str)
        if not id_grupo and not codigo:
            return 'Credenciales no proporcionadas', 400
        grupo = crud.obtener_grupo_by_id(id_grupo, codigo)
        return jsonify(grupo)
    elif request.method == 'POST':
        nombre = request.form.get('nombre')
        id_admin = request.form.get('admin_id')
        public = bool(request.form.get('public'))
        if not all([nombre, id_admin, public != None]):
            return 'Faltan datos', 400
        grupo = crud.crear_grupo(nombre, id_admin, public)
        return {'Info': 'Created Group'}, 200
    elif request.method == 'PUT':
        id_usuario = request.form.get('usuario_id', type=int)
        id_grupo = request.form.get('grupo_id', type=int)

        if not id_usuario or not id_grupo:
            return {'error': 'Faltan datos'}, 400
        resultado = crud.unir_usuario_a_grupo(id_usuario, id_grupo)
        if resultado:
            return {'mensaje': 'Usuario unido al grupo correctamente'}, 200
        else:
            return {'error': 'El usuario ya está en el grupo o ocurrió un error'}, 400
    elif request.method == 'DELETE':
        usuario_id = request.args.get('usuario_id', type=int)
        grupo_id = request.args.get('grupo_id', type=int)
        if not usuario_id or not grupo_id:
            return {'error': 'Faltan datos'}, 400
        resultado = crud.salirse_de_un_grupo(usuario_id, grupo_id)
        if not resultado:
            return {'error': 'Algo salió mal'}
        return {'mensaje': 'Se unió al grupo'}

    
@app.route('/assets/<folder>/<filename>')
def static_images(folder, filename):
    asset_directory = os.path.join('assets', folder)
    return send_from_directory(asset_directory, filename)

@app.route('/.well-known/assetlinks.json')
def assetlinks():
    return jsonify(links_json)

uptime_bot = Bot(service_url, 40)

if __name__ == '__main__':
    uptime_bot.iniciar()
    app.run(host='0.0.0.0', port=8080, debug=True)