# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import get_settings

s = get_settings()
engine = create_engine(s.DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()