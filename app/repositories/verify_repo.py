from sqlalchemy.orm import Session
from app.models import EmailVerification

class SqlAlchemyVerifyRepo:
    def __init__(self, db: Session): self.db = db
    def create(self, ev: EmailVerification) -> None:
        self.db.add(ev); self.db.commit()
    def get(self, token: str):
        return self.db.get(EmailVerification, token)
    def consume(self, token: str) -> None:
        ev = self.db.get(EmailVerification, token)
        if ev: ev.consumed = True; self.db.commit()
