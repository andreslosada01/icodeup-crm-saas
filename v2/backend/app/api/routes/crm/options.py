from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.roles import PLATFORM_ADMIN
from app.db.session import get_db
from app.models import CommunicationChannel, Project, Tenant, TypificationNode, User
from app.schemas.crm import CommunicationChannelOut, CrmOption, CrmOptions
from app.schemas.typification import TypificationOut

from .access import business_tenant_query, ensure_read_access, is_platform


router = APIRouter()


@router.get("/options", response_model=CrmOptions)
def options(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> CrmOptions:
    ensure_read_access(user)
    if is_platform(user) and tenant_id:
        tenant = db.get(Tenant, tenant_id)
        if tenant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")
        tenants = [tenant]
    else:
        tenants = list(db.scalars(business_tenant_query(db))) if is_platform(user) else [db.get(Tenant, user.tenant_id)]
    tenant_ids = [tenant.id for tenant in tenants if tenant]
    projects = list(db.scalars(select(Project).where(Project.tenant_id.in_(tenant_ids)).order_by(Project.name))) if tenant_ids else []
    users = list(db.scalars(select(User).where(User.tenant_id.in_(tenant_ids), User.role != PLATFORM_ADMIN).order_by(User.name))) if tenant_ids else []
    channels = list(db.scalars(select(CommunicationChannel).where(CommunicationChannel.tenant_id.in_(tenant_ids)).order_by(CommunicationChannel.kind, CommunicationChannel.label))) if tenant_ids else []
    return CrmOptions(
        tenants=[CrmOption(id=tenant.id, name=tenant.name) for tenant in tenants if tenant],
        projects=[CrmOption(id=project.id, name=project.name, label=f"{project.code} - {project.name}") for project in projects],
        users=[CrmOption(id=item.id, name=item.name, label=f"{item.name} - {item.role}") for item in users],
        channels=[CommunicationChannelOut.model_validate(channel, from_attributes=True) for channel in channels],
    )


@router.get("/typifications", response_model=list[TypificationOut])
def crm_typifications(
    tenant_id: int | None = None,
    project_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[TypificationNode]:
    ensure_read_access(user)
    query = select(TypificationNode).order_by(TypificationNode.sort_order, TypificationNode.label)
    if is_platform(user):
        if tenant_id:
            query = query.where(TypificationNode.tenant_id == tenant_id)
    else:
        query = query.where(TypificationNode.tenant_id == user.tenant_id)
    if project_id:
        query = query.where((TypificationNode.project_id == project_id) | (TypificationNode.project_id.is_(None)))
    return list(db.scalars(query))
