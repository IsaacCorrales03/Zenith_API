from sqlalchemy import create_engine, ForeignKey, Enum, Boolean, Text, func
from sqlalchemy.orm import sessionmaker, mapped_column, Mapped, relationship, declarative_base
from sqlalchemy import Integer, String, JSON, ARRAY, TEXT, BOOLEAN, DateTime
from dotenv import load_dotenv
import enum
from typing import List
from datetime import datetime
import os
from default import *

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
    porcentajes_aprendizaje: Mapped[dict] = mapped_column(JSON(), default=default_preferencias())  # Cambia default_porcentajes si es necesario
    retroalimentacion: Mapped[List[dict]] = mapped_column(ARRAY(JSON), nullable=True, default=list)
    url_foto_perfil: Mapped[str] = mapped_column(String(600), nullable=True, server_default='https://example.com/assets/perfil_usuario/default.webp')

    inscripciones: Mapped[List['Inscripciones']] = relationship("Inscripciones", back_populates="usuario")
    grupos_administrados: Mapped[List['Grupo']] = relationship("Grupo", back_populates="administrador")
    membresias: Mapped[List['Membresia']] = relationship("Membresia", back_populates="usuario")
    cursos_creados: Mapped[List['Curso']] = relationship("Curso", back_populates="autor")

    def __repr__(self):
        return f"<Usuario {self.nombre}>"

    def to_dict(self):
        try:
            cursos_inscritos = [
                {
                    "Course_ID": inscripcion.curso.id,
                    "Course_Name": inscripcion.curso.nombre,
                    "Inscription_Date": inscripcion.fecha_inscripcion.strftime('%d/%m/%Y')
                } for inscripcion in self.inscripciones
            ]

            grupos_miembro = [
                {
                    "Group_ID": membresia.grupo.id,
                    "Group_Name": membresia.grupo.nombre,
                    "Group_Type": "Público" if membresia.grupo.public else "Privado",
                    "Group_Code": membresia.grupo.codigo,
                    "Group_Admin_ID": membresia.grupo.administrador_id,
                    "Group_Admin_Name": membresia.grupo.administrador.nombre if membresia.grupo.administrador else None,
                    "Group_Members": membresia.grupo.miembros,
                    "Membership_Date": membresia.fecha_membresia.strftime('%d/%m/%Y')
                } for membresia in self.membresias
            ]

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
    nombre: Mapped[str] = mapped_column(String(64), nullable=False)
    duracion: Mapped[int] = mapped_column(Integer(), nullable=False)  # duración en minutos u horas
    url_imagen: Mapped[str] = mapped_column(Text(), nullable=True)
    autor_id: Mapped[int] = mapped_column(ForeignKey("Usuarios.id"), nullable=False)

    inscripciones: Mapped[List['Inscripciones']] = relationship("Inscripciones", back_populates="curso")
    capitulos: Mapped[List['Capitulo']] = relationship("Capitulo", back_populates="curso", cascade="all, delete-orphan")
    autor: Mapped['Usuario'] = relationship("Usuario", back_populates="cursos_creados")

    def to_dict(self):
        try:
            # Organizar capítulos por número usando su método to_dict
            capitulos_data = {}
            for cap in self.capitulos:
                capitulos_data[cap.numero] = {
                    "id": cap.id,
                    "nombre": cap.nombre,
                    "lecciones": {
                        i: leccion.to_dict() 
                        for i, leccion in enumerate(cap.lecciones, start=1)
                    }
                }

            # Inscripciones (mantener como está ya que no tiene to_dict)
            inscripciones_data = [
                {
                    "id": inscripcion.id,
                    "usuario_id": inscripcion.usuario_id,
                    "usuario_nombre": inscripcion.usuario.nombre if inscripcion.usuario else None,
                    "fecha_inscripcion": inscripcion.fecha_inscripcion.strftime('%d/%m/%Y') if inscripcion.fecha_inscripcion else None
                }
                for inscripcion in self.inscripciones
            ]

            # Autor
            autor_data = {
                "id": self.autor.id,
                "nombre": self.autor.nombre
            } if self.autor else None

            return {
                "id": self.id,
                "nombre": self.nombre,
                "duracion": self.duracion,
                "url_imagen": self.url_imagen,
                "autor": autor_data,
                "capitulos": capitulos_data,
                "inscripciones": inscripciones_data
            }
        except Exception as e:
            print("Error", e)
            # En caso de error, devuelve info básica
            return {
                "id": self.id,
                "nombre": self.nombre,
                "duracion": self.duracion,
                "autor_id": self.autor_id
            }

class Capitulo(Base):
    __tablename__ = 'Capitulos'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(64), nullable=False)
    numero: Mapped[int] = mapped_column(Integer(), nullable=False)
    curso_id: Mapped[int] = mapped_column(ForeignKey("Cursos.id"), nullable=False)

    curso: Mapped['Curso'] = relationship("Curso", back_populates="capitulos")
    lecciones: Mapped[List['Leccion']] = relationship("Leccion", back_populates="capitulo", cascade="all, delete-orphan")

class Leccion(Base):
    __tablename__ = 'Lecciones'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(64), nullable=False)
    numero: Mapped[str] = mapped_column(Integer(), nullable=False)
    duracion: Mapped[int] = mapped_column(Integer(), nullable=True)
    creditos: Mapped[int] = mapped_column(Integer(), nullable=True)
    tema: Mapped[str] = mapped_column(String(255), nullable=True)
    concepto: Mapped[str] = mapped_column(String(1200), nullable=False)
    capitulo_id: Mapped[int] = mapped_column(ForeignKey("Capitulos.id"), nullable=False)

    capitulo: Mapped['Capitulo'] = relationship("Capitulo", back_populates="lecciones")
    recursos: Mapped[List['Recurso']] = relationship("Recurso", back_populates="leccion", cascade="all, delete-orphan")
    parrafos: Mapped[List['ParrafoExplicativo']] = relationship("ParrafoExplicativo", back_populates="leccion", cascade="all, delete-orphan")
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "numero": self.numero,
            "duracion": self.duracion,
            "creditos": self.creditos,
            "tema": self.tema,
            "concepto": self.concepto,
            "capitulo_id": self.capitulo_id,
            "recursos": [r.to_dict() for r in self.recursos],
            "parrafos": [p.contenido for p in sorted(self.parrafos, key=lambda x: x.orden)]
        }

class ParrafoExplicativo(Base):
    __tablename__ = 'ParrafosExplicativos'

    id: Mapped[int] = mapped_column(primary_key=True)
    contenido: Mapped[str] = mapped_column(String(2000), nullable=False)
    orden: Mapped[int] = mapped_column(Integer(), nullable=False)

    leccion_id: Mapped[int] = mapped_column(ForeignKey("Lecciones.id"), nullable=False)
    leccion: Mapped['Leccion'] = relationship("Leccion", back_populates="parrafos")

class Recurso(Base):
    __tablename__ = "Recursos"

    id: Mapped[int] = mapped_column(primary_key=True)
    leccion_id: Mapped[int] = mapped_column(ForeignKey("Lecciones.id"), nullable=False)

    tipo: Mapped[str] = mapped_column(String(32), nullable=False)      # Visual, Audiovisual, Auditivo, etc.
    afinacion: Mapped[str] = mapped_column(String(32), nullable=False)  # Video, Artículo, Texto, Práctica
    contenido: Mapped[str] = mapped_column(Text, nullable=False) # URL o ruta relativa
    externo: Mapped[bool] = mapped_column(Boolean, default=True)       # True si es un enlace externo
    descripcion: Mapped[str] = mapped_column(String(256), nullable=True)

    leccion: Mapped["Leccion"] = relationship("Leccion", back_populates="recursos")
    
    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "afinacion": self.afinacion,
            "descripcion": self.descripcion,
            "contenido": self.contenido,
            "externo": self.externo
        }

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
    usuario_id: Mapped[int] = mapped_column(ForeignKey("Usuarios.id"), nullable=False)
    curso_id: Mapped[int] = mapped_column(ForeignKey("Cursos.id"), nullable=False)
    fecha_inscripcion: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    usuario: Mapped['Usuario'] = relationship("Usuario", back_populates="inscripciones")
    curso: Mapped['Curso'] = relationship("Curso", back_populates="inscripciones")

class Membresia(Base):
    __tablename__ = 'Membresias'

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey('Usuarios.id'), nullable=False)
    grupo_id: Mapped[int] = mapped_column(ForeignKey('Grupos.id'), nullable=False)
    fecha_membresia: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    usuario: Mapped['Usuario'] = relationship("Usuario", back_populates="membresias")
    grupo: Mapped['Grupo'] = relationship("Grupo", back_populates="membresias")


if __name__ == '__main__':
    Base.metadata.drop_all(Engine)
    Base.metadata.create_all(Engine)
