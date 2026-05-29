from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.schemas.auth import LoginRequest, LoginResponse, UserSession
from app.services.access_control import get_user_profile
from app.services.audit_service import record_audit
from app.services.auth_service import AuthError, authenticate


router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> LoginResponse:
    try:
        token, user = authenticate(db, payload.email, payload.password)
    except AuthError as exc:
        attempted_user = db.scalar(select(User).where(User.email == payload.email.lower()))
        record_audit(
            db,
            attempted_user,
            "auth",
            "login_failed",
            attempted_user.id if attempted_user else None,
            attempted_user.tenant_id if attempted_user else None,
            module="security",
            after={"email": payload.email},
            request=request,
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    profile = get_user_profile(db, user)
    record_audit(db, user, "auth", "login_success", user.id, user.tenant_id, module="security", after={"email": user.email}, request=request)
    db.commit()
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
