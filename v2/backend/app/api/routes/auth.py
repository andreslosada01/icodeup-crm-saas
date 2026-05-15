from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, LoginResponse, UserSession
from app.services.auth_service import AuthError, authenticate


router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    try:
        token, user = authenticate(db, payload.email, payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return LoginResponse(
        access_token=token,
        user=UserSession(
            id=user.id,
            tenant_id=user.tenant_id,
            name=user.name,
            email=user.email,
            role=user.role,
        ),
    )

