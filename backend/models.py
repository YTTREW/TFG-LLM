from sqlalchemy import Column, Integer, String
from .database import Base

class Profesor(Base):
    __tablename__ = "profesores"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="profesor")
    nombre = Column(String)
    apellidos = Column(String)


class Estudiante(Base):
    __tablename__ = "estudiantes"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="estudiante")
    nombre = Column(String)
    apellidos = Column(String)