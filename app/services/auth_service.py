import uuid, datetime as dt, secrets
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.security import hash_password, verify_password
from app.tokens import issue_pair, rotate_refresh, decode_token
from app.models import User, EmailVerification, PasswordReset
from app.repositories.user_repo import SqlAlchemyUserRepo
from app.repositories.refresh_repo import SqlAlchemyRefreshRepo
from app.repositories.verify_repo import SqlAlchemyVerifyRepo
from app.repositories.reset_repo import SqlAlchemyResetRepo

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = SqlAlchemyUserRepo(db)
        self.refresh = SqlAlchemyRefreshRepo(db)
        self.verify = SqlAlchemyVerifyRepo(db)
        self.reset = SqlAlchemyResetRepo(db)

    # --- core ---
    def register(self, email: str, password: str) -> User:
        if self.users.find_by_email(email):
            raise HTTPException(status_code=409, detail="Email already registered")
        u = User(email=email, password_hash=hash_password(password))
        return self.users.save(u)

    def login(self, email: str, password: str) -> tuple[str, str]:
        u = self.users.find_by_email(email)
        if not u or not u.is_active or not verify_password(password, u.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return issue_pair(self.db, u.id)

    def me(self, access_token: str) -> User:
        data = decode_token(access_token)
        if data.get("type") != "access": raise HTTPException(status_code=401, detail="Invalid token type")
        u = self.users.find_by_id(data.get("sub"))
        if not u or not u.is_active: raise HTTPException(status_code=401, detail="User not found")
        return u

    def refresh_tokens(self, refresh_token: str) -> tuple[str, str]:
        return rotate_refresh(self.db, refresh_token)

    # --- session mgmt ---
    def logout(self, refresh_token: str) -> None:
        data = decode_token(refresh_token)
        if data.get("type") != "refresh": raise HTTPException(status_code=401, detail="Invalid refresh")
        jti = data.get("jti")
        self.refresh.revoke(jti)

    def logout_all(self, access_token: str) -> int:
        data = decode_token(access_token)
        if data.get("type") != "access": raise HTTPException(status_code=401, detail="Invalid token type")
        return self.refresh.revoke_all(data.get("sub"))

    def change_password(self, access_token: str, old_pwd: str, new_pwd: str) -> None:
        u = self.me(access_token)
        if not verify_password(old_pwd, u.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password")
        self.users.set_password(u, hash_password(new_pwd))
        # opzionale: revoca tutti i refresh
        self.refresh.revoke_all(u.id)

    # --- email verify ---
    def request_verify(self, email: str) -> str:
        u = self.users.find_by_email(email)
        if not u: return "ok"  # non svelare
        token = secrets.token_urlsafe(32)
        ev = EmailVerification(token=token, user_id=u.id,
                               expires_at=dt.datetime.utcnow() + dt.timedelta(hours=24))
        self.verify.create(ev)
        # TODO: invia email (service esterno); per ora ritorniamo il token
        return token

    def confirm_verify(self, token: str) -> None:
        ev = self.verify.get(token)
        if not ev or ev.consumed or ev.expires_at < dt.datetime.utcnow():
            raise HTTPException(status_code=400, detail="Invalid/expired token")
        u = self.users.find_by_id(ev.user_id)
        if not u: raise HTTPException(status_code=400, detail="User not found")
        u.is_email_verified = True
        self.db.commit()
        self.verify.consume(token)

    # --- password reset ---
    def request_reset(self, email: str) -> str:
        u = self.users.find_by_email(email)
        if not u: return "ok"
        token = secrets.token_urlsafe(32)
        pr = PasswordReset(token=token, user_id=u.id,
                           expires_at=dt.datetime.utcnow() + dt.timedelta(hours=2))
        self.reset.create(pr)
        # TODO: invia email (service esterno); per ora ritorniamo il token
        return token

    def confirm_reset(self, token: str, new_password: str) -> None:
        pr = self.reset.get(token)
        if not pr or pr.consumed or pr.expires_at < dt.datetime.utcnow():
            raise HTTPException(status_code=400, detail="Invalid/expired token")
        u = self.users.find_by_id(pr.user_id)
        if not u: raise HTTPException(status_code=400, detail="User not found")
        self.users.set_password(u, hash_password(new_password))
        self.reset.consume(token)
        # sicurezza: revoca tutti i refresh
        self.refresh.revoke_all(u.id)
