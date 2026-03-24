from sqlalchemy import Column, Date, Float, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base 


class CasoClinico(Base):
    __tablename__ = "casos_clinicos"

    id = Column(Integer, primary_key=True, index=True)
    
    profesor_id = Column(Integer, ForeignKey("profesores.id", ondelete="CASCADE"), nullable=False)
    

    nombre_paciente = Column(String, nullable=False)
    edad = Column(Integer, nullable=False)
    problema_descripcion = Column(Text, nullable=False) 
    
    es_evaluable = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    visible = Column(Boolean, default=True) 
    fecha_entrega = Column(Date, nullable=True) 

    # Relaciones
    profesor = relationship("Profesor", back_populates="casos")
    chats = relationship("Chat", back_populates="caso", cascade="all, delete-orphan")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)

    # Relación con Estudiante
    estudiante_id = Column(
        Integer,
        ForeignKey("estudiantes.id", ondelete="CASCADE"),
        nullable=False
    )
    caso_id = Column(Integer, ForeignKey("casos_clinicos.id", ondelete="CASCADE"), nullable=False)

    title = Column(String, default="Nuevo chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    grade = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    enviado = Column(Boolean, default=False)
    feedback = Column(Text, nullable=True)

    # Relaciones
    caso = relationship("CasoClinico", back_populates="chats")
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