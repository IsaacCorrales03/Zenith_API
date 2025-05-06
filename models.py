from sqlalchemy import create_engine, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker, mapped_column, Mapped, relationship, declarative_base
from sqlalchemy import Integer, String, JSON, ARRAY, TEXT, BOOLEAN, DateTime
from default import *
from dotenv import load_dotenv
import enum
from typing import List
from datetime import datetime
import os
load_dotenv()
# Use postgresql+psycopg2 as the dialect
postgre_uri = os.getenv('SQL_URI')
Engine = create_engine(postgre_uri)

Base = declarative_base()
Session = sessionmaker(bind=Engine)
session = Session()

class EstilosDeAprendizaje(enum.Enum):
    VISUAL = 'Visual'
    KINESTESICO = 'Kinestésico'
    AUDITIVO = 'Auditivo'
    NO_DEFINIDO = 'No Definido'

class Usuario(Base):
    __tablename__ = 'Usuarios'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)
    api_key: Mapped[str] = mapped_column(String(128), nullable=False)
    correo: Mapped[str] = mapped_column(String(48), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    racha: Mapped[int] = mapped_column(Integer(), default=0)
    lecciones: Mapped[int] = mapped_column(Integer(), default=30, server_default='30')
    aprendizaje_principal: Mapped[EstilosDeAprendizaje] = mapped_column(Enum(EstilosDeAprendizaje), default=EstilosDeAprendizaje.NO_DEFINIDO)
    porcentajes_aprendizaje: Mapped[dict] = mapped_column(JSON(), default=default_porcentajes)
    preferencias: Mapped[dict] = mapped_column(JSON(), default=default_preferencias)
    retroalimentacion: Mapped[List[dict]] = mapped_column(ARRAY(JSON), nullable=True, default=list)
    url_foto_perfil: Mapped[str] = mapped_column(String(600), nullable=True, server_default=f'{service_url}/assets/perfil_usuario/default.webp')

    inscripciones: Mapped[List['Inscripciones']] = relationship("Inscripciones", back_populates="usuario")
    grupos_administrados: Mapped[List['Grupo']] = relationship("Grupo", back_populates="administrador")
    membresias: Mapped[List['Membresia']] = relationship("Membresia", back_populates="usuario")

    def __repr__(self):
        return f"<Usuario {self.nombre}>"
    def to_dict(self):
        try:
            # Procesar cursos inscritos
            cursos_inscritos = [
                {
                    "Course_ID": inscripcion.curso.id,
                    "Course_Name": inscripcion.curso.nombre,
                    "Inscription_Date": inscripcion.fecha_inscripcion.strftime('%d/%m/%Y')
                } for inscripcion in self.inscripciones
            ]

            # Procesar grupos
            grupos_miembro = [
                {
                    "Group_ID": grupo.id,
                    "Group_Name": grupo.nombre,
                    "Group_Type": "Público" if grupo.public else "Privado",
                    "Group_Code": grupo.codigo,
                    "Group_Admin_ID": grupo.administrador_id,
                    "Group_Admin_Name": grupo.administrador.nombre if grupo.administrador else None,
                    "Group_Members": grupo.miembros,
                    "Membership_Date": membresia.fecha_membresia.strftime('%d/%m/%Y')
                } for membresia in self.membresias for grupo in [membresia.grupo]
            ]

            # Grupos administrados
            grupos_administrados = [
                {
                    "Group_ID": grupo.id,
                    "Group_Name": grupo.nombre,
                    "Group_Type": "Público" if grupo.public else "Privado"
                } for grupo in self.grupos_administrados
            ]

            return {
                "User_ID": self.id,
                "Username": self.nombre,
                "Email": self.correo,
                "Url_foto_perfil": self.url_foto_perfil,
                "Api_Key": self.api_key,
                "Primary_Learning": self.aprendizaje_principal.value,
                "Streak": self.racha,
                "Lessons": self.lecciones,
                "Learning_Percentages": self.porcentajes_aprendizaje,
                "Preferences": self.preferencias,
                "Enrolled_Courses": cursos_inscritos,
                "Member_Groups": grupos_miembro,
                "Administered_Groups": grupos_administrados,
                "Feedback": self.retroalimentacion
            }
        except Exception as e:
            print(f"Error al convertir usuario a diccionario: {e}")
            return None

class Curso(Base):
    __tablename__ = 'Cursos'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(32), nullable=False)
    duracion: Mapped[int] = mapped_column(Integer(), nullable=False)
    url_imagen: Mapped[str] = mapped_column(TEXT())
    autor_id: Mapped[int] = mapped_column(ForeignKey("Usuarios.id"), nullable=False)
    
    # Relaciones
    inscripciones: Mapped[List['Inscripciones']] = relationship("Inscripciones", back_populates="curso")
    lecciones: Mapped[List['Leccion']] = relationship("Leccion", back_populates="curso", cascade="all, delete-orphan")
    autor: Mapped['Usuario'] = relationship("Usuario", back_populates="cursos_creados")
    
    def to_dict(self):
        try:
            # Proceso de lecciones
            lecciones_data = [
                {
                    "Leccion_ID": leccion.id,
                    "Leccion_Title": leccion.titulo,
                    "Leccion_Duration": leccion.duracion
                } for leccion in self.lecciones
            ]
            
            # Proceso de inscripciones
            inscripciones_data = [
                {
                    "Inscription_ID": inscripcion.id,
                    "User_ID": inscripcion.usuario_id,
                    "User_Name": inscripcion.usuario.nombre if inscripcion.usuario else None,
                    "Inscription_Date": inscripcion.fecha_inscripcion.strftime('%d/%m/%Y') if inscripcion.fecha_inscripcion else None
                } for inscripcion in self.inscripciones
            ]
            
            # Obtener datos del autor
            autor_data = {
                "User_ID": self.autor.id,
                "User_Name": self.autor.nombre
            } if self.autor else None
            
            return {
                "Course_ID": self.id,
                "Course_Name": self.nombre,
                "Course_Duration": self.duracion,
                "Course_Image": self.url_imagen,
                "Course_Author": autor_data,
                "Lessons": lecciones_data,
                "Inscriptions": inscripciones_data
            }
        except Exception as e:
            # En caso de error, devolver un diccionario básico
            return {
                "Course_ID": self.id,
                "Course_Name": self.nombre,
                "Course_Duration": self.duracion,
                "Course_Image": self.url_imagen,
                "Course_Author_ID": self.autor_id
            }

class Leccion(Base):
    __tablename__ = 'Lecciones'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(64), nullable=False)
    duracion: Mapped[int] = mapped_column(Integer(), nullable=False)  # en minutos
    creditos: Mapped[int] = mapped_column(Integer(), nullable=False)
    tema_principal: Mapped[str] = mapped_column(String(128), nullable=False)
    
    # Clave foránea para relacionar con el curso
    curso_id: Mapped[int] = mapped_column(ForeignKey('Cursos.id'))
    
    # Relación con la tabla de Cursos
    curso: Mapped["Curso"] = relationship("Curso", back_populates="lecciones")

class Grupo(Base):
    __tablename__ = 'Grupos'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(32), nullable=False)
    administrador_id: Mapped[int] = mapped_column(ForeignKey('Usuarios.id'))
    public: Mapped[bool] = mapped_column(BOOLEAN(), default=False)
    miembros: Mapped[int] = mapped_column(Integer(), server_default='0', nullable=True)
    codigo: Mapped[str] = mapped_column(String(16), nullable=False)
    url_banner: Mapped[str] = mapped_column(TEXT, nullable=True)

    administrador: Mapped['Usuario'] = relationship("Usuario", back_populates="grupos_administrados")
    membresias: Mapped[List['Membresia']] = relationship("Membresia", back_populates="grupo")

class Inscripciones(Base):
    __tablename__ = 'Inscripciones'

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey('Usuarios.id'))
    id_curso: Mapped[int] = mapped_column(ForeignKey('Cursos.id'))
    fecha_inscripcion: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)

    usuario: Mapped['Usuario'] = relationship("Usuario", back_populates="inscripciones")
    curso: Mapped['Curso'] = relationship("Curso", back_populates="inscripciones")

class Membresia(Base):
    __tablename__ = 'Membresias'

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey('Usuarios.id'))
    id_grupo: Mapped[int] = mapped_column(ForeignKey('Grupos.id'))
    fecha_membresia: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)
    
    usuario: Mapped['Usuario'] = relationship("Usuario", back_populates="membresias")
    grupo: Mapped['Grupo'] = relationship("Grupo", back_populates="membresias")


# Base.metadata.drop_all(Engine)
# Base.metadata.create_all(Engine)