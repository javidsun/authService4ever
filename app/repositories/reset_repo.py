from sqlalchemy.orm import Session
from app.models import PasswordReset

class SqlAlchemyResetRepo:
    def __init__(self, db: Session): self.db = db
    def create(self, pr: PasswordReset) -> None:
        self.db.add(pr); self.db.commit()
    def get(self, token: str):
        return self.db.get(PasswordReset, token)
    def consume(self, token: str) -> None:
        pr = self.db.get(PasswordReset, token)
        if pr: pr.consumed = True; self.db.commit()
