from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    curso = Column(String, nullable=True)  # solo para estudiantes
