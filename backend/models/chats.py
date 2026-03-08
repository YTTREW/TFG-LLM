from sqlalchemy import Column, Float, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base 

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
    grade = Column(Float, nullable=True)  
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