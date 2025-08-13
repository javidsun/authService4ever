from sqlalchemy.orm import Session
from app.models import User
from typing import cast
from sqlalchemy.sql import ColumnElement

class SqlAlchemyUserRepo:
    def __init__(self, db: Session): self.db = db

    def find_by_email(self, email: str):
        return self.db.query(User).filter(
            cast(ColumnElement[bool], User.email == email)
        ).first()

    def find_by_id(self, user_id: str):
        return self.db.query(User).filter(
            cast(ColumnElement[bool], User.id == user_id)
        ).first()

    def save(self, u: User) -> User:
        self.db.add(u); self.db.commit(); self.db.refresh(u); return u

    def set_password(self, u: User, password_hash: str) -> None:
        u.password_hash = password_hash; self.db.commit()

    def disable(self, u: User) -> None:
        u.is_active = False; self.db.commit()
