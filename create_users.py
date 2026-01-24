from passlib.context import CryptContext
from sqlalchemy import create_engine
from backend.database import SessionLocal
from backend.models import Administrador

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

engine = create_engine("postgresql://tfg_user:tfg_password@localhost:5432/tfg_db")
db = SessionLocal()

admin = Administrador(
    username="admin",
    password_hash=pwd_context.hash("admin1234"),
    name="Pedro",
    surname="García",
    role="admin"
)

db.add(admin)
db.commit()
db.close()
print("Admin creado correctamente")

