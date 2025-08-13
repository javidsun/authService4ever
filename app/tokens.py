import uuid, datetime as dt
from typing import Tuple
from jose import jwt, JWTError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .config import get_settings
from .models import RefreshToken

s = get_settings()

def _load_keys():
    with open(s.PRIVATE_KEY_PATH, "rb") as f:
        private = f.read()
    with open(s.PUBLIC_KEY_PATH, "rb") as f:
        public = f.read()
    return private, public

PRIVATE_KEY, PUBLIC_KEY = _load_keys()
ALGORITHM = s.JWT_ALG

def make_access(sub: str) -> str:
    now = dt.datetime.utcnow()
    exp = now + dt.timedelta(minutes=s.ACCESS_EXPIRES_MIN)
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": int(exp.timestamp()), "type": "access"}
    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)

def make_refresh(sub: str, jti: str | None = None) -> Tuple[str, str]:
    now = dt.datetime.utcnow()
    exp = now + dt.timedelta(days=s.REFRESH_EXPIRES_DAYS)
    jti = jti or str(uuid.uuid4())
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": int(exp.timestamp()), "jti": jti, "type": "refresh"}
    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM), jti

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def issue_pair(db: Session, user_id: str) -> tuple[str, str]:
    access = make_access(user_id)
    refresh, jti = make_refresh(user_id)
    db.add(RefreshToken(jti=jti, user_id=user_id, revoked=False))
    db.commit()
    return access, refresh

def rotate_refresh(db: Session, old_refresh: str) -> tuple[str, str]:
    data = decode_token(old_refresh)
    if data.get("type") != "refresh": raise HTTPException(401, "Invalid refresh")
    jti, sub = data.get("jti"), data.get("sub")
    rt = db.get(RefreshToken, jti)
    if rt is None or rt.revoked: raise HTTPException(401, "Refresh revoked")
    rt.revoked = True
    access = make_access(sub)
    new_refresh, new_jti = make_refresh(sub)
    db.add(RefreshToken(jti=new_jti, user_id=sub, revoked=False))
    db.commit()
    return access, new_refresh

def jwks() -> dict:
    return {"keys": [{"kty": "RSA", "alg": ALGORITHM, "use": "sig", "kid": "auth-service-key-1", "pem": PUBLIC_KEY.decode()}]}
