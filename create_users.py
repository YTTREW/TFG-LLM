from passlib.context import CryptContext
from sqlalchemy import create_engine
from backend.database import SessionLocal
from backend.models import Profesor

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

engine = create_engine("postgresql://tfg_user:tfg_password@localhost:5432/tfg_db")
db = SessionLocal()

prof = Profesor(
    username="profesor1",
    password_hash=pwd_context.hash("prof123"),
    nombre="Ana",
    apellidos="García",
    role="profesor"
)

db.add(prof)
db.commit()
db.close()
print("Usuarios creados correctamente")

