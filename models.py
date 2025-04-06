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

    inscripciones: Mapped[List['Inscripciones']] = relationship("Inscripciones", back_populates="usuario")
    grupos_administrados: Mapped[List['Grupo']] = relationship("Grupo", back_populates="administrador")
    membresias: Mapped[List['Membresia']] = relationship("Membresia", back_populates="usuario")

    def __repr__(self):
        return f"<Usuario {self.nombre}>"

class Curso(Base):
    __tablename__ = 'Cursos'

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(32), nullable=False)
    duracion: Mapped[int] = mapped_column(Integer(), nullable=False)
    url_imagen: Mapped[str] = mapped_column(TEXT())
    
    inscripciones: Mapped[List['Inscripciones']] = relationship("Inscripciones", back_populates="curso")

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


Base.metadata.drop_all(Engine)
Base.metadata.create_all(Engine)