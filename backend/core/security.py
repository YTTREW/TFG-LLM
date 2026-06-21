from passlib.context import CryptContext

# Configuración de hashing de contraseñas
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Funcion para verificar la contraseña
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Funcion para hashear la contraseña
def get_password_hash(password):
    return pwd_context.hash(password)