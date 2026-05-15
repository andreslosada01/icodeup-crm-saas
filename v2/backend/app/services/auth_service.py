from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models import User


class AuthError(Exception):
    pass


def authenticate(db: Session, email: str, password: str) -> tuple[str, User]:
    user = db.scalar(select(User).where(User.email == email.lower(), User.status == "active"))
    if user is None or not verify_password(password, user.password_hash):
        raise AuthError("Credenciales invalidas.")
    token = create_access_token(str(user.id), user.tenant_id, user.role)
    return token, user

