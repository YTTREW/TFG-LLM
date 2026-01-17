from .models import User
from .database import SessionLocal
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user.role
