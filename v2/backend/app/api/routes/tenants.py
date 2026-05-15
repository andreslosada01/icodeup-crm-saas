from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_platform_admin
from app.db.session import get_db
from app.models import User
from app.repositories.tenant_repository import TenantRepository
from app.schemas.tenant import TenantCreate, TenantOut


router = APIRouter(dependencies=[Depends(require_platform_admin)])


@router.get("", response_model=list[TenantOut])
def list_tenants(db: Session = Depends(get_db), _: User = Depends(require_platform_admin)) -> list:
    return TenantRepository(db).list()


@router.post("", response_model=TenantOut)
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db), _: User = Depends(require_platform_admin)):
    tenant = TenantRepository(db).create(payload.name, payload.slug, payload.tax_id)
    db.commit()
    db.refresh(tenant)
    return tenant
