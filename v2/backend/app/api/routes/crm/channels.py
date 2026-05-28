from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.config import settings
from app.db.session import get_db
from app.models import CommunicationChannel, Tenant, User
from app.schemas.crm import CommunicationChannelCreate, CommunicationChannelOut

from .access import ensure_manage_access, ensure_read_access, is_platform, project_for_access


router = APIRouter()


@router.get("/channels", response_model=list[CommunicationChannelOut])
def list_channels(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[CommunicationChannelOut]:
    ensure_read_access(user)
    query = select(CommunicationChannel).order_by(CommunicationChannel.kind, CommunicationChannel.label)
    if not is_platform(user):
        query = query.where(CommunicationChannel.tenant_id == user.tenant_id)
    channels = list(db.scalars(query))
    return [CommunicationChannelOut.model_validate(item, from_attributes=True) for item in channels]


@router.post("/channels", response_model=CommunicationChannelOut, status_code=status.HTTP_201_CREATED)
def create_channel(payload: CommunicationChannelCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CommunicationChannelOut:
    ensure_manage_access(user)
    tenant_id = payload.tenant_id if is_platform(user) and payload.tenant_id else user.tenant_id
    tenant = db.get(Tenant, tenant_id)
    if tenant is None or tenant.slug == settings.platform_tenant_slug:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Selecciona una empresa cliente.")
    if payload.project_id:
        project = project_for_access(db, payload.project_id, user)
        if project.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Proyecto fuera de la empresa.")
    if payload.is_default:
        existing = db.scalars(select(CommunicationChannel).where(CommunicationChannel.tenant_id == tenant_id, CommunicationChannel.kind == payload.kind))
        for item in existing:
            item.is_default = False
    channel = CommunicationChannel(
        tenant_id=tenant_id,
        project_id=payload.project_id,
        kind=payload.kind,
        label=payload.label,
        value=payload.value,
        provider=payload.provider,
        is_default=payload.is_default,
        status=payload.status,
        config_json=payload.config_json,
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return CommunicationChannelOut.model_validate(channel, from_attributes=True)
