from fastapi import APIRouter

from app.core.config import settings
from app.db.session import check_database


router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    database = check_database()
    return {
        "ok": True,
        "app": settings.app_name,
        "environment": settings.app_env,
        "port": settings.app_port,
        "database": database,
    }
