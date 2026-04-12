from sqlalchemy import Column, Date, Float, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base 


class ClinicalCase(Base):
    __tablename__ = "clinical_cases"

    id = Column(Integer, primary_key=True, index=True)
    
    professor_id = Column(Integer, ForeignKey("professors.id", ondelete="CASCADE"), nullable=False)

    patient_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    problem_description = Column(Text, nullable=False) 
    
    is_evaluable = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    is_visible = Column(Boolean, default=True) 
    deadline = Column(Date, nullable=True) 

    # Relaciones
    professor = relationship("Professor", back_populates="clinical_cases")
    chats = relationship("Chat", back_populates="clinical_case", cascade="all, delete-orphan")

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)

    # Relación con Estudiante
    student_id = Column(
        Integer,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )
    clinical_case_id = Column(Integer, ForeignKey("clinical_cases.id", ondelete="CASCADE"), nullable=False)

    title = Column(String, default="New chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    grade = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    is_submitted = Column(Boolean, default=False)

    # Relaciones
    student = relationship("Student", back_populates="chats")
    clinical_case = relationship("ClinicalCase", back_populates="chats")
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

    role = Column(String, nullable=False) 
    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    chat = relationship("Chat", back_populates="messages")