from flask import Flask, jsonify, request, render_template,send_from_directory
from flask_cors import CORS
import os
import crud
from werkzeug.utils import secure_filename
from server_strings import *
from bot import Bot
from waitress import serve
import torch
from Zenith import Zenith, cargar_escalador
import numpy as np
from logger_config import get_logger
from default import *

logger = get_logger("ZenithServer")

app = Flask('__main__')
app.secret_key = os.getenv('secret_key')
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Cargar el modelo y escalador al iniciar el servidor
logger.info("Inicializando el modelo Zenith...")
# Cargar el escalador utilizado durante el entrenamiento
try:
    escalador = cargar_escalador('escalador_preferencias.pkl')
    logger.info("Escalador cargado correctamente")
except Exception as e:
    logger.error(f"Error al cargar el escalador: {str(e)}")
    raise

# Inicializar el modelo
n_entradas = 30  
modelo = Zenith(n_entradas=n_entradas)
# Cargar los parámetros entrenados
try:
    model_path = os.path.join('modelos', 'zenithQ1.pt')
    modelo.load_state_dict(torch.load(model_path))
    modelo.eval()  # Poner el modelo en modo evaluación
    logger.debug(f"Modelo cargado correctamente desde {model_path}")
except Exception as e:
    logger.error(f"Error al cargar el modelo: {str(e)}")
    raise

def predecir(datos_entrada):
    try:
        # Aplicar el mismo escalado que se usó durante el entrenamiento
        datos_escalados = escalador.transform(datos_entrada)
        
        # Convertir a tensor de PyTorch
        tensor_entrada = torch.from_numpy(datos_escalados).float()
        
        # Realizar la predicción
        with torch.no_grad():  # No necesitamos gradientes para la predicción
            predicciones = modelo(tensor_entrada)
        
        # Convertir el resultado a numpy array
        return predicciones.numpy()
    except Exception as e:
        logger.error(f"Error durante la predicción: {str(e)}")
        raise

# Carpetas de archivos
UPLOAD_FOLDER_BASE = "assets"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER_BASE
UPLOAD_FOLDER_CURSOS = os.path.join(UPLOAD_FOLDER_BASE, "cursos")
UPLOAD_FOLDER_GRUPOS = os.path.join(UPLOAD_FOLDER_BASE, "grupos")
UPLOAD_FOLDER_FOTOS_PERFIL = os.path.join(UPLOAD_FOLDER_BASE, "perfil_usuario")

@app.after_request
def log_response_info(response):
    logger.info(f"{request.method} {request.path} - {response.status}")
    return response

@app.route('/status', methods=['GET'])
def health_check():
    """Endpoint para verificar que el servidor está funcionando"""
    return jsonify({'status': 'ok', 'model': 'Zenith'}), 200

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json

        if not data or 'preferencias' not in data or 'feedback' not in data:
            return jsonify({
                'success': False, 
                'message': 'Los datos deben incluir "preferencias" y "feedback"'
            }), 400

        preferencias = np.array(data['preferencias'], dtype=np.float32)
        feedback = np.array(data['feedback'], dtype=np.float32)

        if len(preferencias) != 15 or len(feedback) != 15:
            return jsonify({
                'success': False, 
                'message': 'Tanto "preferencias" como "feedback" deben tener exactamente 15 valores'
            }), 400

        if not np.isclose(np.sum(preferencias), 100, atol=0.1):
            return jsonify({
                'success': False, 
                'message': 'Las preferencias deben sumar 100'
            }), 400

        datos_entrada = np.concatenate([preferencias, feedback]).reshape(1, -1)
        prediccion = predecir(datos_entrada)[0]

        pred_normalizada = (prediccion / prediccion.sum()) * 100
        pred_redondeada = np.round(pred_normalizada, 1)
        suma_actual = round(np.sum(pred_redondeada), 1)
        diferencia = round(100.0 - suma_actual, 1)

        if diferencia != 0:
            # Indices ordenados por feedback descendente (mejor feedback primero)
            indices_ordenados = np.argsort(-feedback) if diferencia > 0 else np.argsort(feedback)

            for idx in indices_ordenados:
                if diferencia == 0:
                    break

                # Calcular cuánto se puede ajustar sin violar límites
                ajuste = min(abs(diferencia), 100.0)
                if diferencia > 0:
                    # Sumar si no supera 100
                    pred_redondeada[idx] += ajuste
                    diferencia -= ajuste
                else:
                    # Restar si no baja de 0
                    if pred_redondeada[idx] >= ajuste:
                        pred_redondeada[idx] -= ajuste
                        diferencia += ajuste

        # Clipping final para evitar errores
        pred_redondeada = np.clip(pred_redondeada, 0, None)
        pred_redondeada = np.round(pred_redondeada, 1)
        diferencia_final = round(100.0 - np.sum(pred_redondeada), 1)

        # Ajuste mínimo si sigue habiendo diferencia (seguridad extra)
        if diferencia_final != 0:
            idx = np.argmax(feedback) if diferencia_final > 0 else np.argmin(feedback)
            pred_redondeada[idx] += diferencia_final
            pred_redondeada = np.round(pred_redondeada, 1)

        pred_final = pred_redondeada.tolist()

        logger.info(f"Predicción realizada. Suma final: {sum(pred_final):.1f}")
        return jsonify({
            'success': True,
            'predicciones': pred_final,
            'message': 'Predicción ajustada con éxito'
        }), 200

    except Exception as e:
        logger.error(f"Error al procesar la solicitud: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}'
        }), 500


@app.route("/adaptar_leccion", methods=["POST"])
def adaptar_lecciones():
    try:
        data = request.get_json()

        leccion_id = data.get("leccion_id")
        preferencias = data.get("preferencias")

        if not isinstance(preferencias, list) or len(preferencias) != 15:
            logger.warning(f"Preferencias inválidas recibidas: {preferencias}")
            return jsonify({"error": "Preferencias inválidas. Deben ser una lista de 15 valores."}), 400

        if leccion_id is None:
            logger.warning("leccion_id no proporcionado en la request")
            return jsonify({"error": "Falta el leccion_id"}), 400

        leccion = crud.obtener_leccion(leccion_id)
        
        if not leccion:
            logger.error(f"No se encontró la lección con ID: {leccion_id}")
            return jsonify({"error": "No se encontraron lecciones para el capítulo dado."}), 404

        resultado = []
        recursos = leccion['recursos']
        adaptados = []

        puntaje_total = 0

        for recurso in recursos:
            afinacion = recurso.get('afinacion')
            subcat_info = subcategorias_a_indice.get(afinacion)

            if subcat_info:
                indice, _ = subcat_info
                peso = preferencias[indice]
                puntaje_total += peso

                recurso_adaptado = recurso.copy()
                recurso_adaptado["adaptabilidad"] = peso
                adaptados.append(recurso_adaptado)

        adaptabilidad_leccion = min(round(puntaje_total, 2), 100)
        adaptados.sort(key=lambda r: r["adaptabilidad"], reverse=True)
        mejores = adaptados[:3]

        resultado.append({
            "leccion_id": leccion["id"],
            "leccion_nombre": leccion.get("nombre", "Sin nombre"),
            "adaptabilidad_leccion": adaptabilidad_leccion,
            "recursos_adaptados": mejores
        })

        logger.info(f"Lección {leccion_id} adaptada exitosamente con adaptabilidad: {adaptabilidad_leccion}")
        return jsonify(resultado)

    except KeyError as e:
        logger.error(f"Error de clave al adaptar lección {leccion_id}: {str(e)}")
        return jsonify({"error": "Error en los datos de la lección"}), 500
    
    except IndexError as e:
        logger.error(f"Error de índice al adaptar lección {leccion_id}: {str(e)}")
        return jsonify({"error": "Error en el índice de preferencias"}), 500
    
    except Exception as e:
        logger.error(f"Error inesperado al adaptar lección {leccion_id}: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500



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
            print(user)
            if user == 440:
                return jsonify({'error':'El nombre ya está en uso'}), 440
            if user == 441:
                return jsonify({'error':'El correo ya está en uso'}), 441
            if user == 442:
                return jsonify({'error':'El nombre es demasiado largo'}), 442
            return jsonify(user), 201
        except Exception as e:
            return jsonify({'error': f'Error al crear usuario: {str(e)}'}), 500



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("correo")
    password = data.get("password")
    print(data)
    
    if not email or not password:
        return jsonify({"error": "Faltan credenciales"}), 400
    
    resultado = crud.iniciar_sesion(email, password)
    if resultado == 401:
        return jsonify({"error": "Credenciales incorrectas"}), 401
    elif resultado == 500:
        return jsonify({"error": "Error interno del servidor"}), 500
    
    return jsonify(resultado), 200

@app.route('/cursos', methods=['POST', 'GET', 'PUT', 'DELETE', 'OPTIONS'])
def cursos():
    if request.method == 'OPTIONS':
        return '', 200
    if request.method == 'GET':
        id_curso = request.args.get('id', type=int)
        if not id_curso:
            cursos = crud.obtener_cursos()
            cursos_list = []
            for curso in cursos:
                cursos_list.append(curso.to_dict())
            return jsonify(cursos_list)
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
        curso_autor = request.form.get('autor')
        if not curso_name or not curso_duracion or not curso_imagen:
            return jsonify({"error": "Faltan datos obligatorios"}), 400
        filename = secure_filename(curso_imagen.filename)
        image_path = os.path.join(UPLOAD_FOLDER_CURSOS, filename)
        curso_imagen.save(image_path)
        img_url = f'{service_url}/{image_path}'
        curso = crud.crear_curso(nombre=curso_name, duracion=curso_duracion,autor_id=curso_autor, url_imagen=img_url)
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

@app.route('/set_user_preferences', methods= ['POST'])
def set_preferences():
    logger.info("Choi homelo chino")
    id = request.args.get('id')
    key = request.args.get('key')
    preferences = request.get_json() 
    resultado = crud.set_preferences(id, key, preferences)
    if resultado:
        print(resultado)
        return jsonify({'Success': 'Se establecieron las nuevas preferencias'})
    else:
        return jsonify({'Error': 'unknown'})

@app.route('/grupos', methods=['POST', 'GET', 'LINK', 'DELETE', 'UNLINK'])
def grupos():
    if request.method == 'GET':
        send_all = request.args.get('all', type=bool)
        if send_all:
            return jsonify(crud.obtener_grupos())
        id_grupo = request.args.get('id', type=int)
        codigo = request.args.get('codigo', type=str)
        if not id_grupo and not codigo:
            return 'Credenciales no proporcionadas', 400
        grupo = crud.obtener_grupo_by_id(id_grupo, codigo)
        return jsonify(grupo)
    elif request.method == 'POST':
        if not request.content_type.startswith('multipart/form-data'):
            return jsonify({"error": "La solicitud debe ser multipart/form-data"}), 400
        nombre = request.form.get('nombre')
        id_admin = request.form.get('admin_id')
        public = bool(request.form.get('public'))
        banner = request.files.get('imagen')
        if not all([nombre, id_admin, banner, public != None]):
            return 'Faltan datos', 400
        filename = secure_filename(banner.filename)
        image_path = os.path.join(UPLOAD_FOLDER_GRUPOS, filename)
        banner.save(image_path)
        banner_url = f'{service_url}/{image_path}'
        grupo = crud.crear_grupo(nombre, id_admin, public, banner_url)
        return {'Info': 'Created Group'}, 200
    elif request.method == 'LINK':
        id_usuario = request.form.get('usuario_id', type=int)
        id_grupo = request.form.get('grupo_id', type=int)

        if not id_usuario or not id_grupo:
            return {'error': 'Faltan datos'}, 400
        resultado = crud.unir_usuario_a_grupo(id_usuario, id_grupo)
        if resultado:
            return {'mensaje': 'Usuario unido al grupo correctamente'}, 200
        else:
            return {'error': 'El usuario ya está en el grupo o ocurrió un error'}, 400
    elif request.method == 'UNLINK':
        usuario_id = request.args.get('usuario_id', type=int)
        grupo_id = request.args.get('grupo_id', type=int)
        if not usuario_id or not grupo_id:
            return {'error': 'Faltan datos'}, 400
        resultado = crud.salirse_de_un_grupo(usuario_id, grupo_id)
        if not resultado:
            return {'error': 'Algo salió mal'}
        return {'mensaje': 'Se sacó al grupo'}
    elif request.method == 'DELETE':
        id_grupo = request.args.get('grupo_id', type=int)
        admin_id = request.args.get('admin_id', type=int)
        if not admin_id or not id_grupo:
            return jsonify({'error': 'Faltan datos'})
        resultado = crud.eliminar_grupo(id_grupo, admin_id)
        if not resultado:
            return jsonify({'error': 'No existe el grupo o no tienes permiso para eliminarlo'})
        return jsonify({'success': 'Grupo eliminado'})

@app.route('/assets/<folder>/<filename>')
def static_images(folder, filename):
    asset_directory = os.path.join('assets', folder)
    return send_from_directory(asset_directory, filename)

@app.route('/change_profile_picture', methods=['POST'])
def change_profile_picture():
    if request.method == 'POST':
        id_user = request.args.get('id_usuario')
        imagen = request.files.get('imagen')
        if not imagen:
            return {'error': 'No se brindó ninguna imagen'}
        filename = secure_filename(imagen.filename)
        image_path = os.path.join(UPLOAD_FOLDER_FOTOS_PERFIL, filename)
        imagen_url = f'{service_url}/{image_path}'
        crud.cambiar_foto()

@app.route('/.well-known/assetlinks.json')
def assetlinks():
    return jsonify(links_json)

if __name__ == '__main__':
    uptime_bot = Bot(service_url, 40)
    uptime_bot.iniciar()
    host = '0.0.0.0'
    port = 1900
    logger.warning(f"Servidor iniciado en: http://{host}:{port}")

    serve(app, host=host, port=port, threads=4)

    logger.critical("Servidor detenido")