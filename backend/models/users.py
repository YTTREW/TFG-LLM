from sqlalchemy import Column, Integer, String, DateTime
from ..core.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

# Modelos para profesores, estudiantes, administradores y tokens de sesión
class Professor(Base):
    __tablename__ = "professors"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="profesor")
    name = Column(String)
    surname = Column(String)

    clinical_cases = relationship("ClinicalCase", back_populates="professor", cascade="all, delete-orphan")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="estudiante")
    name = Column(String)
    surname = Column(String)

    chats = relationship("Chat", back_populates="student", cascade="all, delete-orphan")

class Administrator(Base):
    __tablename__ = "administrators"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    role = Column(String, default="admin", nullable=False)


class SessionToken(Base):
    __tablename__ = "session_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, index=True)
    username = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
