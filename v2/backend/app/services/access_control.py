from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.roles import AGENT, COORDINATOR, PLATFORM_ADMIN, QUALITY_SUPERVISOR, TENANT_ADMIN
from app.db.session import get_db
from app.models import Module, Permission, Role, RolePermission, Tenant, TenantModule, User, UserProfile


ROLE_PERMISSION_FALLBACKS = {
    PLATFORM_ADMIN: {"*"},
    TENANT_ADMIN: {
        "tenant.manage", "tenant.settings.view", "tenant.settings.configure",
        "users.manage", "users.view", "users.create", "users.update", "users.assign",
        "roles.manage", "roles.view", "roles.create", "roles.update", "roles.configure",
        "modules.view", "crm.read", "crm.manage", "crm.dashboard.view",
        "crm.clients.view", "crm.clients.create", "crm.clients.update", "crm.clients.export", "crm.clients.import",
        "crm.activities.view", "crm.activities.create",
        "parties.view", "parties.create", "parties.update", "parties.export",
        "collections.read", "collections.manage", "collections.queue.view",
        "collections.promises.view", "collections.promises.create", "collections.promises.update", "collections.promises.export",
        "collections.payments.view", "collections.payments.create", "collections.payments.export",
        "collections.agreements.view", "collections.agreements.create", "collections.agreements.update", "collections.agreements.export",
        "legal.read", "legal.manage", "legal.cases.view", "legal.cases.create", "legal.cases.update", "legal.cases.export", "legal.deadlines.view",
        "documents.read", "documents.manage", "documents.view", "documents.create", "documents.update", "documents.export",
        "sales.manage", "sales.leads.view", "sales.leads.create", "sales.leads.update", "sales.leads.export",
        "sales.opportunities.view", "sales.opportunities.create", "sales.opportunities.update", "sales.opportunities.export",
        "typifications.view", "typifications.manage", "typifications.trees.manage", "typifications.combinations.manage",
        "recordings.view", "recordings.playback", "recordings.download", "recordings.manage", "recordings.audit.view",
        "uploads.view", "uploads.manage", "uploads.repartos.manage", "uploads.demographics.manage", "uploads.download",
        "demographics.view", "demographics.manage",
        "excel_web.view", "excel_web.query", "excel_web.export", "excel_web.views.manage",
        "reports.view", "reports.export", "integrations.channels.view", "integrations.channels.create", "integrations.channels.update",
        "integrations.providers.view", "integrations.providers.manage", "integrations.templates.view", "integrations.templates.manage",
        "integrations.webhooks.view", "integrations.webhooks.manage", "integrations.events.view",
        "audit.logs.view", "audit.logs.export", "menu.view",
        "configuration.view", "configuration.manage", "configuration.catalogs.manage", "configuration.rules.manage",
        "configuration.alerts.manage", "configuration.workflows.manage", "alerts.view", "alerts.manage",
    },
    COORDINATOR: {
        "crm.manage", "crm.read", "crm.dashboard.view", "crm.clients.view", "crm.clients.create", "crm.clients.update", "crm.clients.import",
        "crm.activities.view", "crm.activities.create",
        "parties.view", "parties.create", "parties.update",
        "collections.manage", "collections.read", "collections.queue.view",
        "collections.promises.view", "collections.promises.create", "collections.promises.update",
        "collections.payments.view", "collections.payments.create",
        "collections.agreements.view", "collections.agreements.create", "collections.agreements.update",
        "legal.manage", "legal.read", "legal.cases.view", "legal.cases.create", "legal.cases.update", "legal.deadlines.view",
        "documents.manage", "documents.read", "documents.view", "documents.create", "documents.update",
        "sales.manage", "sales.leads.view", "sales.leads.create", "sales.leads.update", "sales.opportunities.view", "sales.opportunities.create", "sales.opportunities.update",
        "typifications.view", "recordings.view", "recordings.playback", "uploads.view", "uploads.repartos.manage", "uploads.demographics.manage", "demographics.view", "excel_web.view", "excel_web.query",
        "reports.view", "reports.export", "menu.view", "alerts.view",
    },
    QUALITY_SUPERVISOR: {
        "crm.read", "crm.dashboard.view", "crm.clients.view", "parties.view",
        "collections.read", "collections.queue.view", "collections.promises.view", "collections.payments.view", "collections.agreements.view",
        "crm.activities.view", "typifications.view", "recordings.view", "recordings.playback", "demographics.view", "excel_web.view", "excel_web.query",
        "legal.read", "legal.cases.view", "legal.deadlines.view", "documents.read", "documents.view",
        "reports.view", "menu.view",
        "alerts.view",
    },
    AGENT: {
        "crm.read", "crm.manage_own", "crm.dashboard.view", "crm.clients.view", "crm.clients.update", "crm.activities.view", "crm.activities.create",
        "parties.view", "collections.read", "collections.manage_own", "collections.queue.view",
        "collections.promises.view", "collections.promises.create", "collections.promises.update",
        "collections.payments.view", "collections.payments.create", "collections.agreements.view", "collections.agreements.create",
        "documents.read", "documents.view", "documents.create",
        "typifications.view", "demographics.view", "excel_web.view", "excel_web.query", "excel_web.views.manage",
        "menu.view",
        "alerts.view",
    },
}


def get_user_profile(db: Session, user: User) -> UserProfile | None:
    return db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))


def get_profile_role(db: Session, user: User) -> Role | None:
    profile = get_user_profile(db, user)
    if not profile or not profile.role_id:
        return None
    role = db.get(Role, profile.role_id)
    if role is None or not role.is_active:
        return None
    return role


def get_profile_role_code(db: Session, user: User) -> str | None:
    role = get_profile_role(db, user)
    return role.code if role else None


def is_platform_admin(db: Session, user: User) -> bool:
    profile = get_user_profile(db, user)
    return user.role == PLATFORM_ADMIN or bool(profile and profile.is_platform_admin)


def is_company_admin(db: Session, user: User) -> bool:
    profile = get_user_profile(db, user)
    return user.role == TENANT_ADMIN or bool(profile and profile.is_company_admin)


def sync_user_profile(db: Session, user: User) -> UserProfile:
    legacy_role = db.scalar(select(Role).where(Role.tenant_id.is_(None), Role.code == user.role))
    profile = get_user_profile(db, user)
    if profile is None:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
    current_role = db.get(Role, profile.role_id) if profile.role_id else None
    profile.tenant_id = user.tenant_id
    if legacy_role and (
        profile.role_id is None
        or (current_role is not None and current_role.tenant_id is None and current_role.code in ROLE_PERMISSION_FALLBACKS)
    ):
        profile.role_id = legacy_role.id
    profile.is_platform_admin = user.role == PLATFORM_ADMIN
    profile.is_company_admin = user.role == TENANT_ADMIN
    profile.status = user.status
    return profile


def get_current_tenant(db: Session, user: User) -> Tenant:
    tenant = db.get(Tenant, user.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario sin empresa valida.")
    return tenant


def require_tenant(db: Session, user: User, tenant_id: int | None = None) -> Tenant:
    tenant = get_current_tenant(db, user)
    if is_platform_admin(db, user):
        if tenant_id:
            target = db.get(Tenant, tenant_id)
            if target is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")
            return target
        return tenant
    if tenant_id and tenant_id != tenant.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado por aislamiento de empresa.")
    return tenant


def user_has_module(db: Session, user: User, module_code: str, tenant_id: int | None = None) -> bool:
    if is_platform_admin(db, user):
        return True
    tenant = require_tenant(db, user, tenant_id)
    if module_code in {"core", "administration"} and is_company_admin(db, user):
        return True
    module_count = db.scalar(select(func.count(TenantModule.id)).where(TenantModule.tenant_id == tenant.id)) or 0
    if module_count == 0:
        return True
    module = db.scalar(select(TenantModule).where(TenantModule.tenant_id == tenant.id, TenantModule.module_code == module_code))
    return bool(module and module.is_enabled and module.enabled)


def get_user_permissions(db: Session, user: User) -> set[str]:
    if is_platform_admin(db, user):
        return {"*"}
    profile = get_user_profile(db, user)
    if profile and profile.role_id:
        role = db.get(Role, profile.role_id)
        if role is not None and role.is_active:
            return set(
                db.scalars(
                    select(Permission.code)
                    .join(RolePermission, Permission.id == RolePermission.permission_id)
                    .where(RolePermission.role_id == role.id)
                )
            )
    return set(ROLE_PERMISSION_FALLBACKS.get(user.role, set()))


def user_has_permission(db: Session, user: User, permission_code: str) -> bool:
    permissions = get_user_permissions(db, user)
    return "*" in permissions or permission_code in permissions


def require_module(db: Session, user: User, module_code: str, tenant_id: int | None = None) -> None:
    if not user_has_module(db, user, module_code, tenant_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Modulo no contratado o inactivo para la empresa.")


def require_permission(db: Session, user: User, permission_code: str) -> None:
    if not user_has_permission(db, user, permission_code):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permiso insuficiente.")


def require_active_module(module_code: str):
    def dependency(db: Session = Depends(get_db), user: User = Depends(current_user)) -> User:
        require_module(db, user, module_code)
        return user

    return dependency


def require_permission_dependency(permission_code: str):
    def dependency(db: Session = Depends(get_db), user: User = Depends(current_user)) -> User:
        require_permission(db, user, permission_code)
        return user

    return dependency


def validate_record_belongs_to_tenant(record: Any, tenant_id: int, field: str = "tenant_id") -> None:
    record_tenant_id = getattr(record, field, None)
    if record_tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Registro fuera de la empresa autenticada.")


def module_by_code(db: Session, module_code: str) -> Module | None:
    return db.scalar(select(Module).where(Module.code == module_code))
