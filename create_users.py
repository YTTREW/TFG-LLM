from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base, User

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

engine = create_engine("postgresql://tfg_user:tfg_password@localhost:5432/tfg_db")
Session = sessionmaker(bind=engine)
session = Session()

# Solo un profesor y un estudiante
usuarios = [
    {"username": "profesor1", "password": "prof123", "role": "profesor", "nombre": "Ana", "apellidos": "García"},
    {"username": "estudiante1", "password": "est123", "role": "estudiante", "nombre": "Luis", "apellidos": "Pérez"}
]

for u in usuarios:
    hashed = pwd_context.hash(u["password"])
    user = User(username=u["username"], password_hash=hashed, role=u["role"],
                nombre=u["nombre"], apellidos=u["apellidos"])
    session.add(user)

session.commit()
session.close()
print("Usuarios creados correctamente")

