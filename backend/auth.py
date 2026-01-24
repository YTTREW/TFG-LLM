from .models import Profesor, Estudiante, Administrador
from .database import SessionLocal
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    db = SessionLocal()

    # Buscar en profesores
    profesor = db.query(Profesor).filter_by(username=username).first()
    if profesor and verify_password(password, profesor.password_hash):
        db.close()
        return "profesor"

    # Buscar en estudiantes
    estudiante = db.query(Estudiante).filter_by(username=username).first()
    if estudiante and verify_password(password, estudiante.password_hash):
        db.close()
        return "estudiante"
    
    admin = db.query(Administrador).filter_by(username=username).first()
    if admin and verify_password(password, admin.password_hash):
        db.close()
        return "admin"

    db.close()
    return None
