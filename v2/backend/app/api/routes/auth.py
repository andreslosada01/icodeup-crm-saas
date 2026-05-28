from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, LoginResponse, UserSession
from app.services.access_control import get_user_profile
from app.services.auth_service import AuthError, authenticate


router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    try:
        token, user = authenticate(db, payload.email, payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    profile = get_user_profile(db, user)
    return LoginResponse(
        access_token=token,
        user=UserSession(
            id=user.id,
            tenant_id=user.tenant_id,
            tenant_name=user.tenant.name if user.tenant else None,
            tenant_slug=user.tenant.slug if user.tenant else None,
            name=user.name,
            email=user.email,
            role=user.role,
            is_platform_admin=bool(profile and profile.is_platform_admin) or user.role == "platform_admin",
            is_company_admin=bool(profile and profile.is_company_admin) or user.role == "tenant_admin",
            logo_url=user.tenant.logo_url if user.tenant else None,
            primary_color=user.tenant.primary_color if user.tenant else None,
            secondary_color=user.tenant.secondary_color if user.tenant else None,
        ),
    )
