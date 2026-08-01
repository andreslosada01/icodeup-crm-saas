from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import User
from app.services.menu_service import build_menu, public_branding


router = APIRouter()


@router.get("/me")
def my_menu(
    operational_tenant_id: int | None = None,
    operational_audience: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict:
    return build_menu(db, user, operational_tenant_id=operational_tenant_id, operational_audience=operational_audience)


@router.get("/branding")
def branding(slug: str | None = None, db: Session = Depends(get_db)) -> dict:
    return public_branding(db, slug)
