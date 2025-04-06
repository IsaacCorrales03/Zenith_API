from sqlalchemy.exc import IntegrityError
from psycopg2.errors import StringDataRightTruncation
import re
from criptografic import PasswordManager, generate_api_key, generate_group_link
from models import session, Usuario, Curso, Grupo, Inscripciones, Membresia

def crear_usuario(nombre: str, correo: str, password: str):
    """
    Crear un nuevo usuario en la base de datos.
    
    :param nombre: Nombre del usuario
    :param correo: Correo electrónico del usuario
    :param password: Contraseña del usuario
    :return: Objeto Usuario creado o None si hay error
    """
    nuevo_usuario = Usuario(
        nombre=nombre,
        api_key=generate_api_key(),
        correo=correo,
        password =PasswordManager.hash_password(password),
    )
    try:
        session.add(nuevo_usuario)
        session.commit()
        return nuevo_usuario
    except IntegrityError as error:
        session.rollback()
        # Si el error es de tipo 'UniqueViolation', extraemos el detalle
        if "duplicate key value violates unique constraint" in str(error):
            # Intentamos obtener el campo que causó la violación
            detail_match = re.search(r'DETAIL:\s*Key\s*\((\w+)\)=\((\w+)\)', str(error))
            if detail_match:
                violated_field = detail_match.group(1)
                violated_value = detail_match.group(2)
                error = f"Error: El campo '{violated_field}' con el valor '{violated_value}' ya existe."
                print(error)
                return 400
            else:
                print(f"Error de integridad: {error}")
        else:
            print(f"Error de integridad: {error}")
        return None
    except StringDataRightTruncation as e:
        session.rollback()
        print(e)
        return 401

def crear_curso(nombre: str, duracion: int, url_imagen: str = ""):
    """
    Crear un nuevo curso en la base de datos.
    
    :param nombre: Nombre del curso
    :param duracion: Duración del curso en horas
    :param url_imagen: URL de la imagen del curso (opcional)
    :return: Objeto Curso creado o None si hay error
    """
    try:
        # Verificar si el curso ya existe
        curso_existente = session.query(Curso).filter(Curso.nombre == nombre).first()
        if curso_existente:
            print(f"El curso {nombre} ya existe.")
            return curso_existente
        
        nuevo_curso = Curso(
            nombre=nombre,
            duracion=duracion,
            url_imagen=url_imagen or "https://placeholder.com/curso.jpg"
        )
        
        session.add(nuevo_curso)
        session.commit()
        print(f"Curso {nombre} creado exitosamente.")
        return nuevo_curso
    
    except Exception as e:
        session.rollback()
        print(f"Error al crear curso: {e}")
        return None

def crear_grupo(nombre: str, administrador_id: str, es_publico: bool = False):
    """
    Crear un nuevo grupo en la base de datos.
    
    :param nombre: Nombre del grupo
    :param administrador_nombre: Nombre del usuario administrador
    :param es_publico: Indica si el grupo es público
    :return: Objeto Grupo creado o None si hay error
    """
    try:
        # Buscar al administrador
        administrador = session.query(Usuario).filter(Usuario.id == administrador_id).first()
        if not administrador:
            print(f"No se encontró el usuario {administrador_id}")
            return None
        
        # Verificar si el grupo ya existe
        grupo_existente = session.query(Grupo).filter(Grupo.nombre == nombre).first()
        if grupo_existente:
            print(f"El grupo {nombre} ya existe.")
            return grupo_existente
        
        nuevo_grupo = Grupo(
            nombre=nombre,
            administrador_id=administrador.id,
            public=es_publico,
            codigo=generate_group_link()
        )
        
        session.add(nuevo_grupo)
        session.commit()
        print(f"Grupo {nombre} creado exitosamente.")
        return nuevo_grupo
    
    except Exception as e:
        session.rollback()
        print(f"Error al crear grupo: {e}")
        return None

def obtener_usuario_by_id(id, api_key):
    """
    Obtener información detallada de un usuario por su ID y API key.
    
    :param id: ID del usuario
    :param api_key: API key del usuario
    :return: Diccionario con información del usuario o None si no se encuentra
    """
    try:
        usuario = session.query(Usuario).filter(Usuario.id == id,  Usuario.api_key == api_key).first()
        
        if usuario is None:
            print(f"No se encontró un usuario con el ID {id}")
            return None

        # Procesar cursos inscritos
        cursos_inscritos = [
            {
                "Course_ID": inscripcion.curso.id,
                "Course_Name": inscripcion.curso.nombre,
                "Inscription_Date": inscripcion.fecha_inscripcion.strftime('%d/%m/%Y')
            } for inscripcion in usuario.inscripciones
        ]

        # Procesar grupos
        grupos_miembro = [
            {
                "Group_ID": membresia.grupo.id,
                "Group_Name": membresia.grupo.nombre,
                "Group_Type": "Público" if membresia.grupo.public else "Privado",
                "Group_Admin": membresia.grupo.administrador.nombre,
                "Membership_Date": membresia.fecha_membresia.strftime('%d/%m/%Y')
            } for membresia in usuario.membresias
        ]

        # Grupos administrados
        grupos_administrados = [
            {
                "Group_ID": grupo.id,
                "Group_Name": grupo.nombre,
                "Group_Type": "Público" if grupo.public else "Privado"
            } for grupo in usuario.grupos_administrados
        ]

        user_dict = {
            "User_ID": usuario.id,
            "Username": usuario.nombre,
            "Email": usuario.correo,
            "Api_Key": usuario.api_key,
            "Primary_Learning": usuario.aprendizaje_principal.value,
            "Streak": usuario.racha,
            "Lessons": usuario.lecciones,
            "Learning_Percentages": usuario.porcentajes_aprendizaje,
            "Preferences": usuario.preferencias,
            "Enrolled_Courses": cursos_inscritos,
            "Member_Groups": grupos_miembro,
            "Administered_Groups": grupos_administrados,
            "Feedback": usuario.retroalimentacion
        }
        
        return user_dict
    except Exception as e:
        print(f"Error al obtener usuario: {e}")
        return None

def obtener_curso_by_id(id):
    try:
        curso = session.query(Curso).filter(Curso.id == id).first()
        if curso is None:
            print(f"No se encontró un usuario con el ID {id}")
            return None

        curso_dict = {
            'Curso_id': curso.id,
            'Nombre_Curso': curso.nombre,
            'Duracion': curso.duracion,
            'URL_Img': curso.url_imagen
        }
        return curso_dict
    except Exception as e:
        print(f"Error al obtener el Curso: {e}")
        return None

def obtener_grupo_by_id(id, codigo):
    try:
        print(codigo)
        grupo = session.query(Grupo).filter(Grupo.id == id).first() if id else session.query(Grupo).filter(Grupo.codigo == codigo).first()
        if not grupo:
            return None
        grupo_dict = {
            'Grupo_ID': grupo.id,
            'Nombre': grupo.nombre,
            'Administrador': grupo.administrador.nombre,
            'Miembros': grupo.miembros,
            'Is_public': grupo.public,
            'codigo': grupo.codigo
        }
        return grupo_dict
    except Exception as e:
            print(f"Error al obtener el Grupo: {e}")
            return None

def inscribir_usuario_a_curso(id_usuario: int, id_curso: int):
    """
    Inscribir un usuario a un curso.
    
    :param nombre_usuario: Nombre del usuario
    :param nombre_curso: Nombre del curso
    :return: Objeto Inscripciones o None si hay error
    """
    try:
        # Buscar usuario
        usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
        if not usuario:
            print(f"No se encontró el usuario {id_usuario}")
            return None
        
        # Buscar curso
        curso = session.query(Curso).filter(Curso.id == id_curso).first()
        if not curso:
            print(f"No se encontró el curso {id_curso}")
            return None
        
        # Verificar si ya está inscrito
        inscripcion_existente = session.query(Inscripciones).filter(
            Inscripciones.id_usuario == usuario.id,
            Inscripciones.id_curso == curso.id
        ).first()
        
        if inscripcion_existente:
            print(f"{id_usuario} ya está inscrito en {id_curso}")
            return inscripcion_existente
        
        # Crear nueva inscripción
        nueva_inscripcion = Inscripciones(
            id_usuario=usuario.id,
            id_curso=curso.id
        )
        
        session.add(nueva_inscripcion)
        session.commit()
        print(f"{id_usuario} inscrito en {id_curso} exitosamente.")
        return nueva_inscripcion
    
    except Exception as e:
        session.rollback()
        print(f"Error al inscribir usuario: {e}")
        return None

def unir_usuario_a_grupo(id_usuario: int, id_grupo: int):
    """
    Agregar un usuario a un grupo.
    
    :param nombre_usuario: Nombre del usuario
    :param nombre_grupo: Nombre del grupo
    :return: Objeto Membresia o None si hay error
    """
    try:
        # Buscar usuario
        usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
        if not usuario:
            print(f"No se encontró el usuario {id_usuario}")
            return None
        
        # Buscar grupo
        grupo = session.query(Grupo).filter(Grupo.id == id_grupo).first()
        if not grupo:
            print(f"No se encontró el grupo {id_grupo}")
            return None
        
        # Verificar si ya es miembro
        membresia_existente = session.query(Membresia).filter(
            Membresia.id_usuario == usuario.id,
            Membresia.id_grupo == grupo.id
        ).first()
        
        if membresia_existente:
            print(f"{id_usuario} ya es miembro de {id_grupo}")
            return membresia_existente
        
        # Crear nueva membresía
        nueva_membresia = Membresia(
            id_usuario=usuario.id,
            id_grupo=grupo.id
        )
        
        session.add(nueva_membresia)
        session.commit()
        print(f"{usuario.nombre} se unió a {grupo.nombre} exitosamente.")
        return nueva_membresia
    
    except Exception as e:
        session.rollback()
        print(f"Error al unir usuario a grupo: {e}")
        return None

def darse_de_baja_de_un_curso(id_usuario, id_curso):
    try:
        inscripcion = session.query(Inscripciones).filter(Inscripciones.id_usuario == id_usuario, Inscripciones.id_curso == id_curso).first()
        if inscripcion:
            session.delete(inscripcion)
            session.commit()
            return True
        else:
            return False
    except Exception as e:
        session.rollback()
        print(f"Error al darse de baja: {str(e)}")
        return False

def salirse_de_un_grupo(id_usuario, id_grupo):
    try:
        membresia = session.query(Membresia).filter(Membresia.id_usuario == id_usuario, Membresia.id_grupo == id_grupo).first()
        if membresia:
            session.delete(membresia)
            session.commit()
            return True
        else:
            return False
    except Exception as e:
        session.rollback()
        print(f"Error al salirse de un grupo: {str(e)}")
        return False


def iniciar_sesion(email, password):
    """
    Login endpoint for user authentication.
        "correo": "user@example.com",
        "password": "userpassword"    
    Returns:
    - Success: User details and API key (200)
    - Error: Error message (400 or 401)
    """
    try:
        
        # Buscar usuario por correo usando SQLAlchemy
        usuario = session.query(Usuario).filter(Usuario.correo == email).first()
        
        # Verificar si el usuario existe
        if not usuario:
            return 401
        if PasswordManager.verify_password(password, usuario.password):
            return usuario
        else:
            return 401
    
    except Exception as e:
        # Manejo de errores
        session.rollback()
        return 500
    finally:
        # Cerrar la sesión de SQLAlchemy
        session.close()