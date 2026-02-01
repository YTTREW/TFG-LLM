from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from .database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

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

    chats = relationship(
        "Chat",
        backref="estudiante",
        cascade="all, delete-orphan"
    )

class Administrador(Base):
    __tablename__ = "administradores"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    role = Column(String, default="admin", nullable=False)

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)

    # Relación con Estudiante
    estudiante_id = Column(
        Integer,
        ForeignKey("estudiantes.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(String, default="Nuevo chat")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan"
    )

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    chat_id = Column(
        Integer,
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False
    )

    role = Column(String, nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    chat = relationship("Chat", back_populates="messages")


class SessionToken(Base):
    __tablename__ = "session_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, index=True)
    username = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
