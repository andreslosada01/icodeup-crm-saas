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
from app.services.access_control import get_profile_role, get_user_permissions, is_company_admin, is_platform_admin, require_permission, require_tenant, user_has_permission
from app.services.audit_service import record_audit
from app.services.menu_service import build_menu


router = APIRouter()

RESERVED_PERMISSION_CODES = {"modules.configure", "health.view"}
CRITICAL_PERMISSION_CODES = {
    "users.create",
    "users.update",
    "users.assign",
    "roles.manage",
    "roles.configure",
    "modules.configure",
    "audit.logs.view",
    "crm.clients.export",
    "collections.payments.export",
    "tenant.settings.configure",
}
ADMIN_PERMISSION_PREFIXES = ("platform.",)
MODULE_PERMISSION_LABELS = {
    "core": "Core SaaS",
    "administration": "Administracion",
    "crm": "Collects 360",
    "collections": "Collects 360 · Cobranzas",
    "legal": "Juridico",
    "documents": "Documentos",
    "sales": "Pipeline comercial",
    "bi": "Analytics 360",
    "integrations": "ChatBOX 360",
}


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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Permisos reservados para IEP: {', '.join(sorted(restricted))}")


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


def module_permission_codes(db: Session, module_code: str) -> set[str]:
    return set(db.scalars(select(Permission.code).where(Permission.module_code == module_code)))


def module_primary_roles(db: Session, tenant_id: int, module_code: str) -> list[str]:
    rows = (
        select(Role.name)
        .join(RolePermission, Role.id == RolePermission.role_id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .where(Permission.module_code == module_code)
        .where((Role.tenant_id.is_(None)) | (Role.tenant_id == tenant_id))
        .distinct()
        .order_by(Role.name)
        .limit(6)
    )
    return list(db.scalars(rows))


def users_with_module_access(db: Session, tenant_id: int, module_code: str) -> int:
    permission_codes = module_permission_codes(db, module_code)
    count = 0
    for tenant_user in db.scalars(select(User).where(User.tenant_id == tenant_id, User.status == "active")):
        user_permissions = get_user_permissions(db, tenant_user)
        if "*" in user_permissions or permission_codes.intersection(user_permissions):
            count += 1
    return count


def module_deactivation_impact(module: Module, users_with_access: int, related_permissions: int) -> str:
    if users_with_access:
        return f"Desactivar {module.name} ocultaria capacidades a {users_with_access} usuarios con permisos relacionados."
    if related_permissions:
        return f"Desactivar {module.name} no afectaria usuarios actuales, pero bloquearia {related_permissions} permisos configurados."
    return f"Desactivar {module.name} no tiene usuarios con acceso detectado."


def module_commercial_recommendation(module: Module, enabled: bool) -> str:
    if enabled:
        return "Modulo activo. Revisar roles con acceso y adopcion operativa."
    if module.code in {"legal", "documents", "bi", "integrations"}:
        return "Modulo candidato a activacion comercial segun madurez de la operacion."
    return "Solicitar activacion a Icodeup Advisors si la empresa requiere esta capacidad."


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


def is_reserved_permission(code: str) -> bool:
    return code.startswith(ADMIN_PERMISSION_PREFIXES) or code in RESERVED_PERMISSION_CODES


def is_critical_permission(code: str) -> bool:
    return code in CRITICAL_PERMISSION_CODES or code.endswith(".export") or code.startswith("platform.")


def visible_permission_codes(db: Session, viewer: User, target: User) -> set[str]:
    codes = get_user_permissions(db, target)
    if "*" in codes:
        codes = set(db.scalars(select(Permission.code)))
    if not is_platform_admin(db, viewer):
        codes = {code for code in codes if not is_reserved_permission(code)}
    return codes


def permission_rows(db: Session, viewer: User, target: User) -> list[dict]:
    codes = visible_permission_codes(db, viewer, target)
    if not codes:
        return []
    permissions = list(db.scalars(select(Permission).where(Permission.code.in_(codes)).order_by(Permission.module_code, Permission.code)))
    known = {permission.code for permission in permissions}
    rows = [
        {
            "code": permission.code,
            "name": permission.name,
            "module_code": permission.module_code or "core",
            "critical": is_critical_permission(permission.code),
        }
        for permission in permissions
    ]
    for code in sorted(codes - known):
        rows.append({"code": code, "name": code, "module_code": "legacy", "critical": is_critical_permission(code)})
    return rows


def grouped_permissions(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["module_code"] or "core", []).append(row)
    return grouped


def user_effective_role(db: Session, target: User) -> Role | None:
    return get_profile_role(db, target)


def profile_label(role: Role | None, target: User) -> str:
    return role.name if role else ROLE_LABELS.get(target.role, target.role)


def module_access_rows(db: Session, viewer: User, target: User, permission_codes: set[str], menu_payload: dict | None = None) -> list[dict]:
    tenant_modules = {item.module_code: item for item in db.scalars(select(TenantModule).where(TenantModule.tenant_id == target.tenant_id))}
    menu_payload = menu_payload or build_menu(db, target)
    visible_module_codes = {item.get("module_code") or "core" for item in menu_payload.get("items", [])}
    permission_modules = {
        permission.module_code or "core"
        for permission in db.scalars(select(Permission).where(Permission.code.in_(permission_codes))) if permission.module_code
    }
    rows = []
    for module in db.scalars(select(Module).order_by(Module.order, Module.name)):
        tenant_module = tenant_modules.get(module.code)
        active = bool(module.is_active and tenant_module and tenant_module.enabled and tenant_module.is_enabled)
        visible = module.code in visible_module_codes
        has_permissions = module.code in permission_modules or "*" in permission_codes
        if not is_platform_admin(db, viewer) and module.code in {"hr", "finance", "industrial"} and not active:
            continue
        rows.append(
            {
                "code": module.code,
                "name": module.name,
                "description": module.description,
                "category": module.category,
                "active": active,
                "contracted": bool(tenant_module),
                "visible": visible,
                "has_permissions": has_permissions,
                "status": "visible" if visible else "blocked" if active else "inactive",
                "reason": module_visibility_reason(module, active, visible, has_permissions),
            }
        )
    return rows


def module_visibility_reason(module: Module, active: bool, visible: bool, has_permissions: bool) -> str:
    if visible:
        return f"Visible porque {module.name} esta activo y el perfil tiene permisos del modulo."
    if not active:
        return f"Oculto porque {module.name} no esta activo para este tenant."
    if not has_permissions:
        return f"Oculto porque el rol efectivo no tiene permisos de {module.name}."
    return "Oculto por audiencia de menu o restriccion del perfil."


def restrictions_for_user(db: Session, target: User, permission_codes: set[str], effective_role: Role | None) -> list[str]:
    restrictions = ["No puede ver informacion de otros tenants."]
    role_code = effective_role.code if effective_role else target.role
    if not any(code.endswith(".export") for code in permission_codes) and "*" not in permission_codes:
        restrictions.append("No tiene permisos de exportacion.")
    if role_code in {"collections_agent", "agent"}:
        restrictions.append("Operacion limitada a clientes/casos asignados segun endpoint.")
    if role_code == "lawyer":
        restrictions.append("Vista concentrada en juridico y documentos de casos asignados.")
    if role_code == "sales_advisor":
        restrictions.append("Vista concentrada en ventas asignadas y clientes en lectura.")
    if role_code == "tenant_auditor":
        restrictions.append("Perfil de lectura y auditoria sin gestion operativa.")
    if user_has_permission(db, target, "roles.configure") or user_has_permission(db, target, "users.assign"):
        restrictions.append("Puede modificar configuracion sensible de usuarios o roles.")
    return restrictions


def risk_flags_for_user(db: Session, target: User, permission_codes: set[str], effective_role: Role | None) -> list[dict]:
    flags = []
    critical = sorted(code for code in permission_codes if is_critical_permission(code))
    if "*" in permission_codes:
        flags.append({"severity": "critical", "label": "Acceso platform", "detail": "Tiene acceso total por perfil platform."})
    if critical:
        flags.append({"severity": "high", "label": "Permisos criticos", "detail": f"{len(critical)} permisos sensibles activos."})
    if target.role in {"coordinator", "tenant_admin"} and effective_role and effective_role.tenant_id is None:
        flags.append({"severity": "medium", "label": "Rol legacy amplio", "detail": "Usa rol legacy amplio sin perfil tenant especializado."})
    if target.status != "active" and critical:
        flags.append({"severity": "high", "label": "Usuario inactivo sensible", "detail": "Usuario inactivo conserva permisos criticos."})
    if not flags:
        flags.append({"severity": "low", "label": "Sin alertas criticas", "detail": "No se detectaron permisos sensibles en el perfil efectivo."})
    return flags


def recommendation_for_user(target: User, effective_role: Role | None, risk_flags: list[dict]) -> str:
    role_code = effective_role.code if effective_role else target.role
    severities = {flag["severity"] for flag in risk_flags}
    if role_code == "lawyer":
        return "Este perfil esta correctamente limitado para gestion juridica."
    if role_code == "sales_advisor":
        return "Este perfil esta correctamente limitado para gestion comercial."
    if "critical" in severities or "high" in severities:
        return "Revisar permisos criticos antes de operar en produccion."
    if effective_role and effective_role.tenant_id is not None:
        return "Perfil funcional configurado por tenant con permisos granulares."
    return "Este usuario conserva permisos por rol legacy; revisar si debe migrarse a rol especializado."


def effective_access_payload(db: Session, viewer: User, target: User) -> dict:
    tenant = db.get(Tenant, target.tenant_id)
    effective_role = user_effective_role(db, target)
    permission_items = permission_rows(db, viewer, target)
    permission_codes = {item["code"] for item in permission_items}
    menu_payload = build_menu(db, target)
    modules = module_access_rows(db, viewer, target, permission_codes, menu_payload)
    restrictions = restrictions_for_user(db, target, permission_codes, effective_role)
    risk_flags = risk_flags_for_user(db, target, permission_codes, effective_role)
    leader = db.get(User, target.leader_id) if target.leader_id else None
    return {
        "user": {
            "id": target.id,
            "name": target.name,
            "email": target.email,
            "status": target.status,
            "title": target.title,
            "phone": target.phone,
            "leader_id": target.leader_id,
            "leader_name": leader.name if leader else None,
        },
        "tenant": {
            "id": tenant.id if tenant else target.tenant_id,
            "name": tenant.name if tenant else "Tenant no encontrado",
            "slug": tenant.slug if tenant else None,
        },
        "legacy_role": {
            "code": target.role,
            "label": ROLE_LABELS.get(target.role, target.role),
            "description": "Rol tecnico heredado para compatibilidad con modulos antiguos.",
        },
        "specialized_role": {
            "id": effective_role.id if effective_role else None,
            "code": effective_role.code if effective_role else None,
            "name": effective_role.name if effective_role else None,
            "description": effective_role.description if effective_role else None,
            "is_system_role": effective_role.is_system_role if effective_role else False,
            "scope": "tenant" if effective_role and effective_role.tenant_id else "system" if effective_role else "legacy_fallback",
        },
        "business_profile": profile_label(effective_role, target),
        "permissions": permission_items,
        "permission_groups": grouped_permissions(permission_items),
        "permission_count": len(permission_items),
        "critical_permissions": [item for item in permission_items if item["critical"]],
        "modules": modules,
        "visible_sections": menu_payload.get("items", []),
        "hidden_sections": hidden_section_reasons(modules),
        "restrictions": restrictions,
        "risk_flags": risk_flags,
        "recommendation": recommendation_for_user(target, effective_role, risk_flags),
    }


def hidden_section_reasons(modules: list[dict]) -> list[dict]:
    return [
        {"module_code": item["code"], "module": item["name"], "reason": item["reason"]}
        for item in modules
        if not item["visible"]
    ]


def user_for_governance_access(db: Session, viewer: User, user_id: int) -> User:
    if not (is_platform_admin(db, viewer) or is_company_admin(db, viewer)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores pueden consultar perfiles efectivos.")
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    target_tenant(db, viewer, target.tenant_id)
    return target


def insight(severity: str, title: str, description: str, action: str, entity_type: str, entity_id: int | None = None) -> dict:
    return {
        "severity": severity,
        "title": title,
        "description": description,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
    }


def tenant_scope_for_insights(db: Session, user: User) -> list[Tenant]:
    if not (is_platform_admin(db, user) or is_company_admin(db, user)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores pueden consultar alertas de seguridad.")
    if is_platform_admin(db, user):
        return list(db.scalars(select(Tenant).where(Tenant.slug != settings.platform_tenant_slug).order_by(Tenant.name)))
    return [target_tenant(db, user)]


def security_insights_for_tenant(db: Session, tenant: Tenant) -> list[dict]:
    rows: list[dict] = []
    tenant_users = list(db.scalars(select(User).where(User.tenant_id == tenant.id).order_by(User.name)))
    for item in tenant_users:
        role = user_effective_role(db, item)
        permissions = get_user_permissions(db, item)
        if item.role in {"coordinator", "tenant_admin"} and role and role.tenant_id is None:
            rows.append(insight("medium", "Usuario con rol legacy amplio", f"{item.name} opera con {item.role} sin rol tenant especializado.", "Revisar migracion a rol especializado.", "user", item.id))
        export_permissions = sorted(code for code in permissions if code.endswith(".export") or code == "*")
        if export_permissions:
            rows.append(insight("high", "Usuario con permisos de exportacion", f"{item.name} tiene {len(export_permissions)} permisos de exportacion o acceso total.", "Validar necesidad operacional y auditoria.", "user", item.id))
        if item.status != "active" and any(is_critical_permission(code) for code in permissions):
            rows.append(insight("high", "Usuario inactivo con permisos criticos", f"{item.name} esta inactivo y conserva permisos sensibles.", "Retirar permisos o desactivar perfil.", "user", item.id))
    for role in db.scalars(select(Role).where((Role.tenant_id.is_(None)) | (Role.tenant_id == tenant.id)).order_by(Role.name)):
        codes = role_permission_codes(db, role.id)
        if any(code in {"users.create", "users.update", "roles.configure", "modules.configure"} or code.startswith("platform.") for code in codes):
            rows.append(insight("medium", "Rol con administracion sensible", f"{role.name} contiene permisos administrativos.", "Revisar asignaciones antes de produccion.", "role", role.id))
    for module_status in db.scalars(select(TenantModule).where(TenantModule.tenant_id == tenant.id, TenantModule.enabled.is_(True), TenantModule.is_enabled.is_(True))):
        if users_with_module_access(db, tenant.id, module_status.module_code) == 0:
            rows.append(insight("low", "Modulo activo sin usuarios", f"{module_status.module_code} esta activo pero no tiene usuarios con permisos relacionados.", "Asignar roles o evaluar desactivacion.", "module", module_status.id))
    subscription = db.scalar(select(TenantSubscription).where(TenantSubscription.tenant_id == tenant.id, TenantSubscription.status.in_(["trial", "active"])))
    if subscription is None:
        rows.append(insight("medium", "Tenant sin plan activo", f"{tenant.name} no tiene suscripcion trial/activa detectada.", "Regularizar plan comercial o documentar excepcion.", "tenant", tenant.id))
    if settings.enable_demo_data or settings.enable_demo_seeds or tenant.slug.endswith("-demo") or "demo" in tenant.slug:
        rows.append(insight("low", "Data demo activa", f"{tenant.name} parece operar con datos o tenant demo.", "Validar que no se use como ambiente productivo.", "tenant", tenant.id))
    return rows


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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Los roles de sistema solo los modifica IEP SuperAdmin.")
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Los roles de sistema solo los modifica IEP SuperAdmin.")
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
        enabled = bool(tenant_module.enabled) if tenant_module else False
        is_enabled = bool(tenant_module.is_enabled) if tenant_module else False
        related_permission_count = db.scalar(select(func.count(Permission.id)).where(Permission.module_code == module.code)) or 0
        critical_permission_count = db.scalar(select(func.count(Permission.id)).where(Permission.module_code == module.code, Permission.code.in_(CRITICAL_PERMISSION_CODES))) or 0
        users_count = users_with_module_access(db, tenant.id, module.code)
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
                enabled=enabled,
                is_enabled=is_enabled,
                configuration_json=tenant_module.configuration_json if tenant_module else None,
                related_permission_count=related_permission_count,
                critical_permission_count=critical_permission_count,
                users_with_access=users_count,
                primary_roles=module_primary_roles(db, tenant.id, module.code),
                deactivation_impact=module_deactivation_impact(module, users_count, related_permission_count),
                commercial_recommendation=module_commercial_recommendation(module, enabled and is_enabled),
            )
        )
    return rows


@router.put("/modules/{tenant_id}", response_model=list[ModuleStatusOut])
def update_module_status(tenant_id: int, payload: list[TenantModuleToggle], db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[ModuleStatusOut]:
    if not is_platform_admin(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo IEP SuperAdmin puede activar o desactivar modulos contratados.")
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
    limit: int = Query(default=20, ge=1, le=20),
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
def list_parties(q: str | None = None, tenant_id: int | None = None, limit: int = Query(default=20, ge=1, le=20), db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[Party]:
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo IEP SuperAdmin ve el inventario comercial global.")
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


@router.get("/security-insights")
def list_security_insights(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[dict]:
    rows: list[dict] = []
    for tenant in tenant_scope_for_insights(db, user):
        rows.extend(security_insights_for_tenant(db, tenant))
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return sorted(rows, key=lambda item: (severity_order.get(item["severity"], 9), item["title"]))[:80]


@router.get("/users/{user_id}/effective-access")
def get_user_effective_access(user_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    target = user_for_governance_access(db, user, user_id)
    return effective_access_payload(db, user, target)


@router.get("/users/{user_id}/access-explanation")
def get_user_access_explanation(user_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    target = user_for_governance_access(db, user, user_id)
    payload = effective_access_payload(db, user, target)
    return {
        "user": payload["user"],
        "visible_sections": payload["visible_sections"],
        "hidden_sections": payload["hidden_sections"],
        "modules": payload["modules"],
        "restrictions": payload["restrictions"],
        "recommendation": payload["recommendation"],
    }


@router.get("/users")
def list_tenant_users(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[dict]:
    require_permission(db, user, "users.view")
    tenant = target_tenant(db, user, tenant_id)
    rows = []
    query = select(User).where(User.tenant_id == tenant.id).order_by(User.name)
    for item in db.scalars(query):
        profile = db.scalar(select(UserProfile).where(UserProfile.user_id == item.id))
        role = db.get(Role, profile.role_id) if profile and profile.role_id else None
        permissions = visible_permission_codes(db, user, item)
        menu_payload = build_menu(db, item)
        visible_modules = sorted({menu_item.get("module_code") or "core" for menu_item in menu_payload.get("items", [])})
        risk_flags = risk_flags_for_user(db, item, permissions, role)
        latest_activity = db.scalar(select(AuditLog.created_at).where(AuditLog.user_id == item.id).order_by(AuditLog.created_at.desc()).limit(1))
        leader = db.get(User, item.leader_id) if item.leader_id else None
        rows.append(
            {
                "id": item.id,
                "tenant_id": item.tenant_id,
                "name": item.name,
                "email": item.email,
                "role": item.role,
                "legacy_role": item.role,
                "legacy_role_label": ROLE_LABELS.get(item.role, item.role),
                "role_id": role.id if role else None,
                "role_name": role.name if role else ROLE_LABELS.get(item.role, item.role),
                "specialized_role_code": role.code if role else None,
                "specialized_role_name": role.name if role else None,
                "specialized_role_scope": "tenant" if role and role.tenant_id else "system" if role else "legacy_fallback",
                "business_profile": profile_label(role, item),
                "status": item.status,
                "leader_id": item.leader_id,
                "leader_name": leader.name if leader else None,
                "phone": item.phone,
                "title": item.title,
                "visible_modules": visible_modules,
                "visible_module_count": len(visible_modules),
                "permission_count": len(permissions),
                "critical_permission_count": len([code for code in permissions if is_critical_permission(code)]),
                "risk_flags": risk_flags,
                "last_activity_at": latest_activity,
            }
        )
    return rows
