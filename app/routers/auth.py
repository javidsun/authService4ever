from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..db import get_db
from ..schemas import RegisterIn, LoginIn, TokensOut, MeOut, ChangePasswordIn, EmailIn, TokenIn
from ..services.auth_service import AuthService
from ..tokens import jwks

router = APIRouter(prefix="/auth", tags=["auth"])

def svc(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

@router.post("/register", response_model=MeOut, status_code=201)
def register(body: RegisterIn, s: AuthService = Depends(svc)):
    u = s.register(str(body.email), body.password)
    return MeOut(id=u.id, email=u.email, is_email_verified=u.is_email_verified, is_active=u.is_active)

@router.post("/login", response_model=TokensOut)
def login(body: LoginIn, s: AuthService = Depends(svc)):
    access, refresh = s.login(str(body.email), body.password)
    return TokensOut(access_token=access, refresh_token=refresh)

@router.get("/me", response_model=MeOut)
def me(authorization: str | None = Header(default=None), s: AuthService = Depends(svc)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    u = s.me(token)
    return MeOut(id=u.id, email=u.email, is_email_verified=u.is_email_verified, is_active=u.is_active)

@router.post("/refresh", response_model=TokensOut)
def refresh(authorization: str | None = Header(default=None), s: AuthService = Depends(svc)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    old_refresh = authorization.split(" ", 1)[1]
    access, new_refresh = s.refresh_tokens(old_refresh)
    return TokensOut(access_token=access, refresh_token=new_refresh)

@router.post("/logout", status_code=204)
def logout(authorization: str | None = Header(default=None), s: AuthService = Depends(svc)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    refresh = authorization.split(" ", 1)[1]
    s.logout(refresh)
    return

@router.post("/logout-all", status_code=204)
def logout_all(authorization: str | None = Header(default=None), s: AuthService = Depends(svc)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    access = authorization.split(" ", 1)[1]
    s.logout_all(access)
    return

@router.post("/change-password", status_code=204)
def change_password(body: ChangePasswordIn, authorization: str | None = Header(default=None), s: AuthService = Depends(svc)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    access = authorization.split(" ", 1)[1]
    s.change_password(access, body.old_password, body.new_password)
    return

@router.post("/verify-email/request", status_code=202)
def verify_request(body: EmailIn, s: AuthService = Depends(svc)):
    token = s.request_verify(str(body.email))
    return {"status": "sent", "dev_token": token}  # in prod non ritornare il token!

@router.post("/verify-email/confirm", status_code=204)
def verify_confirm(body: TokenIn, s: AuthService = Depends(svc)):
    s.confirm_verify(body.token); return

@router.post("/reset-password/request", status_code=202)
def reset_request(body: EmailIn, s: AuthService = Depends(svc)):
    token = s.request_reset(str(body.email))
    return {"status": "sent", "dev_token": token}  # in prod non ritornare il token!

@router.post("/reset-password/confirm", status_code=204)
def reset_confirm(body: dict, s: AuthService = Depends(svc)):
    token = body.get("token"); new_password = body.get("new_password")
    if not token or not new_password:
        raise HTTPException(status_code=400, detail="token and new_password required")
    s.confirm_reset(token, new_password); return

@router.get("/.well-known/jwks.json")
def jwks_endpoint():
    return jwks()
