from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Esta función la tenías en chats.py, pero su sitio correcto es aquí
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
