# API de Zenith AI

Este repositorio contiene una API REST basada en Flask para un sistema de gestión de recursos para el proyecto android Zenith AI. La API proporciona endpoints para la gestión de usuarios, administración de cursos y organización de grupos.

## Tabla de Contenidos
- [Visión General](#visión-general)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Configuración e Instalación](#configuración-e-instalación)
- [Endpoints de la API](#endpoints-de-la-api)
  - [Gestión de Usuarios](#gestión-de-usuarios)
  - [Gestión de Cursos](#gestión-de-cursos)
  - [Gestión de Grupos](#gestión-de-grupos)
- [Manejo de Archivos](#manejo-de-archivos)
- [Seguridad](#seguridad)
- [Características Adicionales](#características-adicionales)

## Visión General

Esta aplicación Flask sirve como backend para una plataforma de aprendizaje donde los usuarios pueden:
- Registrarse y autenticarse
- Explorar e inscribirse en cursos
- Unirse y participar en grupos
- Acceder a materiales y recursos de los cursos

## Estructura del Proyecto

El proyecto se basa en varios componentes clave:

- **Flask**: Framework web para construir la API
- **CORS**: Soporte para Compartir Recursos de Origen Cruzado para la accesibilidad de la API
- **Werkzeug**: Biblioteca de utilidades para el manejo de archivos
- **Módulos personalizados**:
  - `crud.py`: Operaciones de base de datos
  - `server_strings.py`: Cadenas de configuración
  - `bot.py`: Monitoreo automatizado del servicio

## Configuración e Instalación

### Prerrequisitos
- Python 3.x
- Flask y paquetes requeridos
- Variables de entorno para seguridad

### Instalación

1. Clonar el repositorio
2. Instalar paquetes requeridos:
   ```
   pip install -r requirements.txt
   ```
3. Configurar la variable de entorno en el .env con la URI de la base de datos
4. Ejecutar la aplicación:
   ```
   python main.py
   ```

## Endpoints de la API

### Gestión de Usuarios

#### GET `/usuario`
Recupera información del usuario por ID.

**Parámetros:**
- `id` (int): ID del usuario
- `api_key` (str): Clave de autenticación

**Respuestas:**
- `200`: Detalles del usuario
- `400`: Credenciales faltantes
- `404`: Usuario no encontrado
- `500`: Error del servidor

#### POST `/usuario`
Crea un nuevo usuario.

**Cuerpo de la Solicitud:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Respuestas:**
- `201`: Usuario creado exitosamente
- `400`: Datos faltantes/inválidos o nombre de usuario ya en uso
- `500`: Error del servidor

#### POST `/login`
Autentica a un usuario.

**Cuerpo de la Solicitud:**
```json
{
  "correo": "string",
  "password": "string"
}
```

**Respuestas:**
- `200`: Inicio de sesión exitoso, devuelve detalles del usuario y clave API
- `400`: Credenciales faltantes
- `401`: Credenciales incorrectas
- `500`: Error del servidor

### Gestión de Cursos

#### GET `/cursos`
Recupera información del curso por ID.

**Parámetros:**
- `id` (int): ID del curso

**Respuestas:**
- `200`: Detalles del curso
- `400`: Curso no encontrado o ID no especificado

#### POST `/cursos`
Crea un nuevo curso.

**Datos del Formulario:**
- `nombre` (str): Nombre del curso
- `duracion` (int): Duración del curso
- `imagen` (archivo): Imagen del curso

**Respuestas:**
- `200`: Curso creado exitosamente
- `400`: Datos faltantes o tipo de contenido incorrecto

#### PUT `/cursos`
Inscribe a un usuario en un curso.

**Datos del Formulario:**
- `usuario_id` (int): ID del usuario
- `curso_id` (int): ID del curso

**Respuestas:**
- `200`: Inscripción exitosa
- `400`: Error durante la inscripción o datos faltantes

#### DELETE `/cursos`
Desvincula a un usuario de un curso.

**Parámetros:**
- `usuario_id` (int): ID del usuario
- `curso_id` (int): ID del curso

**Respuestas:**
- `200`: Baja exitosa
- `400`: Error durante la baja o datos faltantes

### Gestión de Grupos

#### GET `/grupos`
Recupera información del grupo por ID o código.

**Parámetros:**
- `id` (int): ID del grupo (opcional)
- `codigo` (str): Código del grupo (opcional)

**Respuestas:**
- `200`: Detalles del grupo
- `400`: Parámetros faltantes

#### POST `/grupos`
Crea un nuevo grupo.

**Datos del Formulario:**
- `nombre` (str): Nombre del grupo
- `admin_id` (int): ID del usuario administrador
- `public` (bool): Indicador de estado público

**Respuestas:**
- `200`: Grupo creado exitosamente
- `400`: Datos faltantes

#### PUT `/grupos`
Añade un usuario a un grupo.

**Datos del Formulario:**
- `usuario_id` (int): ID del usuario
- `grupo_id` (int): ID del grupo

**Respuestas:**
- `200`: Usuario añadido exitosamente
- `400`: Error al añadir usuario o datos faltantes

#### DELETE `/grupos`
Elimina un usuario de un grupo.

**Parámetros:**
- `usuario_id` (int): ID del usuario
- `grupo_id` (int): ID del grupo

**Respuestas:**
- `200`: Usuario eliminado exitosamente
- `400`: Error al eliminar usuario o datos faltantes

## Manejo de Archivos

La aplicación maneja cargas de archivos para materiales de cursos:

- Los archivos se almacenan en el directorio `assets/cursos`
- Los nombres de archivo se aseguran usando `secure_filename` de Werkzeug
- Los archivos se sirven a través del endpoint `/assets/<carpeta>/<nombre_archivo>`

## Seguridad

La aplicación implementa varias medidas de seguridad:

- Clave secreta para la gestión de sesiones
- Autenticación con clave API para la identificación del usuario
- Validación de correo electrónico para el registro
- Manejo de contraseñas (implementación en `crud.py`)

## Características Adicionales

### Monitoreo de Disponibilidad

La aplicación incluye un bot de monitoreo de disponibilidad que ayuda a garantizar la disponibilidad del servicio:
```python
uptime_bot = Bot(service_url, 40)
```

### Integración con Aplicación Android

La aplicación incluye soporte para enlaces profundos de aplicaciones Android a través de:
```
@app.route('/.well-known/assetlinks.json')
def assetlinks():
    return jsonify(links_json)
```

## Ejecución de la Aplicación

La aplicación se ejecuta en el puerto 8080 con el modo de depuración habilitado para desarrollo:
```python
if __name__ == '__main__':
    uptime_bot.iniciar()
    app.run(host='0.0.0.0', port=8080, debug=True)
```

> **Nota:** Para despliegue en producción, deshabilitar el modo de depuración y utilizar el servidor WSGI de producción Gunicorn.