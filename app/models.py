# app/models.py
import uuid, datetime as dt
from sqlalchemy import Column, String, DateTime, Boolean, UniqueConstraint
from .db_base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    jti = Column(String, primary_key=True)              # token id
    user_id = Column(String, index=True, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    __table_args__ = (UniqueConstraint("jti"),)
