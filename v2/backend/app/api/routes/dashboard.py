from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import User
from app.services.dashboard_service import role_dashboard


router = APIRouter()


@router.get("/me")
def my_dashboard(db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    return role_dashboard(db, user)
