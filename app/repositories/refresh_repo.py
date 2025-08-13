from sqlalchemy.orm import Session
from sqlalchemy import update
from app.models import RefreshToken

class SqlAlchemyRefreshRepo:
    def __init__(self, db: Session): self.db = db
    def get(self, jti: str): return self.db.get(RefreshToken, jti)
    def save(self, rt: RefreshToken) -> None:
        self.db.add(rt); self.db.commit()
    def revoke(self, jti: str) -> None:
        rt = self.db.get(RefreshToken, jti)
        if rt: rt.revoked = True; self.db.commit()

    def revoke_all(self, user_id: str) -> int:
        stmt = (
            update(RefreshToken)
            .where(
                (RefreshToken.user_id == user_id) & (RefreshToken.revoked.is_(False))
            )
            .values(revoked=True)
        )
        res = self.db.execute(stmt)
        self.db.commit()
        return int(res.rowcount or 0)
