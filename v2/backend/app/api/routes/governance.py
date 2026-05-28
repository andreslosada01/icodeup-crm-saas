from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.config import settings
from app.core.roles import ROLE_LABELS
from app.db.session import get_db
from app.models import AuditLog, Module, Party, Permission, Role, RolePermission, SaasPlan, Tenant, TenantConfiguration, TenantModule, TenantSubscription, User, UserProfile
from app.schemas.governance import (
    AuditLogOut,
    ModuleStatusOut,
    PartyCreate,
    PartyOut,
    PartyPatch,
    PermissionOut,
    RoleCreate,
    RoleOut,
    RolePatch,
    RolePermissionsUpdate,
    TenantModuleToggle,
    TenantSettingsOut,
    TenantSettingsPatch,
    UserRoleAssign,
)
from app.services.access_control import is_company_admin, is_platform_admin, require_permission, require_tenant, user_has_permission
from app.services.audit_service import record_audit


router = APIRouter()


def target_tenant(db: Session, user: User, tenant_id: int | None = None) -> Tenant:
    return require_tenant(db, user, tenant_id)


def ensure_admin_or_permission(db: Session, user: User, permission_code: str) -> None:
    if is_platform_admin(db, user) or is_company_admin(db, user):
        return
    require_permission(db, user, permission_code)


def role_permission_codes(db: Session, role_id: int) -> list[str]:
    query = (
        select(Permission.code)
        .join(RolePermission, Permission.id == RolePermission.permission_id)
        .where(RolePermission.role_id == role_id)
        .order_by(Permission.module_code, Permission.code)
    )
    return list(db.scalars(query))


def validate_assignable_permissions(user: User, db: Session, permission_codes: list[str]) -> None:
    if is_platform_admin(db, user):
        return
    restricted = [code for code in permission_codes if code.startswith("platform.") or code in {"modules.configure", "health.view"}]
    if restricted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Permisos reservados para Icodeup: {', '.join(sorted(restricted))}")


def role_to_out(db: Session, role: Role) -> RoleOut:
    user_count = db.scalar(select(func.count(UserProfile.id)).where(UserProfile.role_id == role.id)) or 0
    return RoleOut(
        id=role.id,
        tenant_id=role.tenant_id,
        code=role.code,
        name=role.name,
        description=role.description,
        is_system_role=role.is_system_role,
        is_active=role.is_active,
        permission_codes=role_permission_codes(db, role.id),
        user_count=user_count,
    )


def tenant_config_value(db: Session, tenant_id: int, key: str) -> str | None:
    item = db.scalar(select(TenantConfiguration).where(TenantConfiguration.tenant_id == tenant_id, TenantConfiguration.key == key, TenantConfiguration.is_active.is_(True)))
    if not item or item.value_json is None:
        return None
    try:
        return json.loads(item.value_json)
    except json.JSONDecodeError:
        return item.value_json


def set_tenant_config(db: Session, tenant_id: int, key: str, value: str | None) -> None:
    item = db.scalar(select(TenantConfiguration).where(TenantConfiguration.tenant_id == tenant_id, TenantConfiguration.key == key))
    if item is None:
        item = TenantConfiguration(tenant_id=tenant_id, key=key)
        db.add(item)
    item.value_json = json.dumps(value or "")
    item.is_active = True


@router.get("/permissions", response_model=list[PermissionOut])
def list_permissions(module_code: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[Permission]:
    ensure_admin_or_permission(db, user, "roles.view")
    query = select(Permission).order_by(Permission.module_code, Permission.code)
    if module_code:
        query = query.where(Permission.module_code == module_code)
    permissions = list(db.scalars(query))
    if not is_platform_admin(db, user):
        permissions = [item for item in permissions if not item.code.startswith("platform.") and item.code not in {"modules.configure", "health.view"}]
    return permissions


@router.get("/roles", response_model=list[RoleOut])
def list_roles(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[RoleOut]:
    ensure_admin_or_permission(db, user, "roles.view")
    tenant = target_tenant(db, user, tenant_id)
    query = select(Role).where((Role.tenant_id.is_(None)) | (Role.tenant_id == tenant.id)).order_by(Role.is_system_role.desc(), Role.name)
    return [role_to_out(db, item) for item in db.scalars(query)]


@router.post("/roles", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleCreate, tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> RoleOut:
    require_permission(db, user, "roles.create")
    tenant = target_tenant(db, user, tenant_id)
    code = payload.code or payload.name.strip().lower().replace(" ", "_")
    role = Role(tenant_id=tenant.id, code=code, name=payload.name.strip(), description=payload.description, is_system_role=False, is_active=True)
    db.add(role)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un rol con ese codigo en la empresa.") from exc
    validate_assignable_permissions(user, db, payload.permission_codes)
    update_role_permissions_internal(db, role, payload.permission_codes)
    record_audit(db, user, "role", "create", role.id, tenant.id, after={"code": role.code, "name": role.name})
    db.commit()
    db.refresh(role)
    return role_to_out(db, role)


@router.patch("/roles/{role_id}", response_model=RoleOut)
def update_role(role_id: int, payload: RolePatch, db: Session = Depends(get_db), user: User = Depends(current_user)) -> RoleOut:
    require_permission(db, user, "roles.update")
    role = db.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado.")
    if role.is_system_role and not is_platform_admin(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Los roles de sistema solo los modifica Icodeup.")
    if role.tenant_id is not None:
        target_tenant(db, user, role.tenant_id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(role, field, value)
    record_audit(db, user, "role", "update", role.id, role.tenant_id, after=updates)
    db.commit()
    db.refresh(role)
    return role_to_out(db, role)


def update_role_permissions_internal(db: Session, role: Role, permission_codes: list[str]) -> None:
    permissions = list(db.scalars(select(Permission).where(Permission.code.in_(permission_codes)))) if permission_codes else []
    valid_codes = {item.code for item in permissions}
    invalid = sorted(set(permission_codes) - valid_codes)
    if invalid:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Permisos invalidos: {', '.join(invalid)}")
    current = list(db.scalars(select(RolePermission).where(RolePermission.role_id == role.id)))
    target_ids = {item.id for item in permissions}
    current_ids = {item.permission_id for item in current}
    for item in current:
        if item.permission_id not in target_ids:
            db.delete(item)
    for permission in permissions:
        if permission.id not in current_ids:
            db.add(RolePermission(role_id=role.id, permission_id=permission.id))


@router.put("/roles/{role_id}/permissions", response_model=RoleOut)
def update_role_permissions(role_id: int, payload: RolePermissionsUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> RoleOut:
    require_permission(db, user, "roles.configure")
    role = db.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado.")
    if role.is_system_role and not is_platform_admin(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Los roles de sistema solo los modifica Icodeup.")
    if role.tenant_id is not None:
        target_tenant(db, user, role.tenant_id)
    validate_assignable_permissions(user, db, payload.permission_codes)
    update_role_permissions_internal(db, role, payload.permission_codes)
    record_audit(db, user, "role_permission", "update", role.id, role.tenant_id, after={"permission_codes": payload.permission_codes})
    db.commit()
    db.refresh(role)
    return role_to_out(db, role)


@router.put("/users/{user_id}/role")
def assign_user_role(user_id: int, payload: UserRoleAssign, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "users.assign")
    target = db.get(User, user_id)
    role = db.get(Role, payload.role_id)
    if target is None or role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario o rol no encontrado.")
    target_tenant(db, user, target.tenant_id)
    if role.tenant_id not in {None, target.tenant_id}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El rol no pertenece a la empresa del usuario.")
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == target.id))
    if profile is None:
        profile = UserProfile(user_id=target.id, tenant_id=target.tenant_id)
        db.add(profile)
    profile.role_id = role.id
    profile.tenant_id = target.tenant_id
    if role.is_system_role and role.code in ROLE_LABELS:
        target.role = role.code
    record_audit(db, user, "user_role", "assign", target.id, target.tenant_id, after={"role_id": role.id, "role_code": role.code})
    db.commit()
    return {"ok": True, "user_id": target.id, "role_id": role.id, "role_code": role.code}


@router.get("/modules", response_model=list[ModuleStatusOut])
def list_module_status(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[ModuleStatusOut]:
    ensure_admin_or_permission(db, user, "modules.view")
    tenant = target_tenant(db, user, tenant_id)
    configured = {item.module_code: item for item in db.scalars(select(TenantModule).where(TenantModule.tenant_id == tenant.id))}
    rows = []
    for module in db.scalars(select(Module).order_by(Module.order, Module.name)):
        tenant_module = configured.get(module.code)
        rows.append(
            ModuleStatusOut(
                id=module.id,
                code=module.code,
                name=module.name,
                description=module.description,
                category=module.category,
                icon=module.icon,
                order=module.order,
                is_active=module.is_active,
                tenant_module_id=tenant_module.id if tenant_module else None,
                enabled=bool(tenant_module.enabled) if tenant_module else False,
                is_enabled=bool(tenant_module.is_enabled) if tenant_module else False,
                configuration_json=tenant_module.configuration_json if tenant_module else None,
            )
        )
    return rows


@router.put("/modules/{tenant_id}", response_model=list[ModuleStatusOut])
def update_module_status(tenant_id: int, payload: list[TenantModuleToggle], db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[ModuleStatusOut]:
    if not is_platform_admin(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo Icodeup puede activar o desactivar modulos contratados.")
    tenant = target_tenant(db, user, tenant_id)
    configured = {item.module_code: item for item in db.scalars(select(TenantModule).where(TenantModule.tenant_id == tenant.id))}
    modules = {item.code: item for item in db.scalars(select(Module))}
    for item in payload:
        if item.module_code not in modules:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Modulo no existe: {item.module_code}")
        tenant_module = configured.get(item.module_code)
        if tenant_module is None:
            tenant_module = TenantModule(tenant_id=tenant.id, module_id=modules[item.module_code].id, module_code=item.module_code)
            db.add(tenant_module)
        tenant_module.enabled = item.enabled
        tenant_module.is_enabled = item.enabled
        tenant_module.configuration_json = item.configuration_json if item.configuration_json is not None else tenant_module.configuration_json
    record_audit(db, user, "tenant_module", "update", tenant.id, tenant.id, after={"modules": [item.model_dump() for item in payload]})
    db.commit()
    return list_module_status(tenant.id, db, user)


@router.get("/settings", response_model=TenantSettingsOut)
def get_tenant_settings(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> TenantSettingsOut:
    ensure_admin_or_permission(db, user, "tenant.settings.view")
    tenant = target_tenant(db, user, tenant_id)
    return TenantSettingsOut(
        tenant_id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        document_type=tenant.document_type,
        document_number=tenant.document_number,
        logo_url=tenant.logo_url,
        primary_color=tenant.primary_color,
        secondary_color=tenant.secondary_color,
        timezone=tenant.timezone,
        login_headline=tenant_config_value(db, tenant.id, "login.headline"),
        login_subheadline=tenant_config_value(db, tenant.id, "login.subheadline"),
    )


@router.patch("/settings", response_model=TenantSettingsOut)
def update_tenant_settings(payload: TenantSettingsPatch, tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> TenantSettingsOut:
    require_permission(db, user, "tenant.settings.configure")
    tenant = target_tenant(db, user, tenant_id)
    updates = payload.model_dump(exclude_unset=True)
    for field in ["name", "document_type", "document_number", "logo_url", "primary_color", "secondary_color", "timezone"]:
        if field in updates:
            setattr(tenant, field, updates[field])
    if "login_headline" in updates:
        set_tenant_config(db, tenant.id, "login.headline", updates["login_headline"])
    if "login_subheadline" in updates:
        set_tenant_config(db, tenant.id, "login.subheadline", updates["login_subheadline"])
    record_audit(db, user, "tenant_settings", "update", tenant.id, tenant.id, after=updates)
    db.commit()
    db.refresh(tenant)
    return get_tenant_settings(tenant.id, db, user)


@router.get("/audit-logs", response_model=list[AuditLogOut])
def list_audit_logs(
    tenant_id: int | None = None,
    module: str | None = None,
    action: str | None = None,
    user_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[AuditLog]:
    require_permission(db, user, "audit.logs.view")
    query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(AuditLog.tenant_id == tenant_id)
    else:
        query = query.where(AuditLog.tenant_id == user.tenant_id)
    if module:
        query = query.where(AuditLog.module == module)
    if action:
        query = query.where(AuditLog.action == action)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if date_from:
        query = query.where(AuditLog.created_at >= date_from)
    if date_to:
        query = query.where(AuditLog.created_at <= date_to)
    return list(db.scalars(query))


@router.get("/parties", response_model=list[PartyOut])
def list_parties(q: str | None = None, tenant_id: int | None = None, limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[Party]:
    require_permission(db, user, "parties.view")
    tenant = target_tenant(db, user, tenant_id)
    query = select(Party).where(Party.tenant_id == tenant.id).order_by(Party.updated_at.desc()).limit(limit)
    if q:
        pattern = f"%{q.lower()}%"
        query = query.where(func.lower(Party.display_name).like(pattern) | func.lower(Party.document_number).like(pattern) | func.lower(Party.email).like(pattern))
    return list(db.scalars(query))


@router.post("/parties", response_model=PartyOut, status_code=status.HTTP_201_CREATED)
def create_party(payload: PartyCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Party:
    require_permission(db, user, "parties.create")
    tenant = target_tenant(db, user, payload.tenant_id)
    party = Party(tenant_id=tenant.id, **payload.model_dump(exclude={"tenant_id"}))
    db.add(party)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un tercero con ese documento en la empresa.") from exc
    record_audit(db, user, "party", "create", party.id, party.tenant_id, after={"display_name": party.display_name, "document_number": party.document_number})
    db.commit()
    db.refresh(party)
    return party


@router.patch("/parties/{party_id}", response_model=PartyOut)
def update_party(party_id: int, payload: PartyPatch, db: Session = Depends(get_db), user: User = Depends(current_user)) -> Party:
    require_permission(db, user, "parties.update")
    party = db.get(Party, party_id)
    if party is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tercero no encontrado.")
    target_tenant(db, user, party.tenant_id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(party, field, value)
    record_audit(db, user, "party", "update", party.id, party.tenant_id, after=updates)
    db.commit()
    db.refresh(party)
    return party


@router.get("/subscriptions")
def list_subscription_overview(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[dict]:
    if not is_platform_admin(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo Icodeup plataforma ve el inventario comercial global.")
    rows = []
    tenants = list(db.scalars(select(Tenant).where(Tenant.slug != settings.platform_tenant_slug).order_by(Tenant.name)))
    for tenant in tenants:
        subscription = db.scalar(select(TenantSubscription).where(TenantSubscription.tenant_id == tenant.id).order_by(TenantSubscription.created_at.desc()))
        plan = db.get(SaasPlan, subscription.plan_id) if subscription else None
        active_modules = db.scalar(select(func.count(TenantModule.id)).where(TenantModule.tenant_id == tenant.id, TenantModule.enabled.is_(True), TenantModule.is_enabled.is_(True))) or 0
        rows.append(
            {
                "tenant_id": tenant.id,
                "tenant_name": tenant.name,
                "plan": plan.name if plan else "Sin plan",
                "status": subscription.status if subscription else "sin_suscripcion",
                "billing_cycle": subscription.billing_cycle if subscription else "-",
                "active_modules": active_modules,
            }
        )
    return rows


@router.get("/users")
def list_tenant_users(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[dict]:
    require_permission(db, user, "users.view")
    tenant = target_tenant(db, user, tenant_id)
    rows = []
    query = select(User).where(User.tenant_id == tenant.id).order_by(User.name)
    for item in db.scalars(query):
        profile = db.scalar(select(UserProfile).where(UserProfile.user_id == item.id))
        role = db.get(Role, profile.role_id) if profile and profile.role_id else None
        rows.append(
            {
                "id": item.id,
                "tenant_id": item.tenant_id,
                "name": item.name,
                "email": item.email,
                "role": item.role,
                "role_id": role.id if role else None,
                "role_name": role.name if role else ROLE_LABELS.get(item.role, item.role),
                "status": item.status,
                "leader_id": item.leader_id,
                "phone": item.phone,
                "title": item.title,
            }
        )
    return rows
