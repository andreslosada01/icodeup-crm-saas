from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


ALGORITHM = "HS256"
MAX_BCRYPT_BYTES = 72


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > MAX_BCRYPT_BYTES:
        raise ValueError("La contrasena no puede superar 72 bytes para bcrypt.")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > MAX_BCRYPT_BYTES:
        return False
    return bcrypt.checkpw(password_bytes, password_hash.encode("utf-8"))


def create_access_token(subject: str, tenant_id: int, role: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(hours=settings.session_hours)
    payload = {
        "sub": subject,
        "tenant_id": tenant_id,
        "role": role,
        "exp": expires,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError:
        return None
