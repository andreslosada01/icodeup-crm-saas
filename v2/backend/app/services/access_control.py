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
    TENANT_ADMIN: {"tenant.manage", "users.manage", "crm.manage", "collections.manage", "legal.manage", "documents.manage", "sales.manage", "reports.view", "menu.view"},
    COORDINATOR: {"crm.manage", "collections.manage", "legal.manage", "documents.manage", "sales.manage", "reports.view", "menu.view"},
    QUALITY_SUPERVISOR: {"crm.read", "collections.read", "legal.read", "documents.read", "reports.view", "menu.view"},
    AGENT: {"crm.read", "crm.manage_own", "collections.read", "collections.manage_own", "documents.read", "sales.read_own", "menu.view"},
}


def get_user_profile(db: Session, user: User) -> UserProfile | None:
    return db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))


def is_platform_admin(db: Session, user: User) -> bool:
    profile = get_user_profile(db, user)
    return user.role == PLATFORM_ADMIN or bool(profile and profile.is_platform_admin)


def is_company_admin(db: Session, user: User) -> bool:
    profile = get_user_profile(db, user)
    return user.role == TENANT_ADMIN or bool(profile and profile.is_company_admin)


def sync_user_profile(db: Session, user: User) -> UserProfile:
    role = db.scalar(select(Role).where(Role.tenant_id.is_(None), Role.code == user.role))
    profile = get_user_profile(db, user)
    if profile is None:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
    profile.tenant_id = user.tenant_id
    profile.role_id = role.id if role else profile.role_id
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


def user_has_permission(db: Session, user: User, permission_code: str) -> bool:
    if is_platform_admin(db, user):
        return True
    fallbacks = ROLE_PERMISSION_FALLBACKS.get(user.role, set())
    if "*" in fallbacks or permission_code in fallbacks:
        return True
    profile = get_user_profile(db, user)
    if not profile or not profile.role_id:
        return False
    return bool(
        db.scalar(
            select(RolePermission.id)
            .join(Permission, Permission.id == RolePermission.permission_id)
            .where(RolePermission.role_id == profile.role_id, Permission.code == permission_code)
        )
    )


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
