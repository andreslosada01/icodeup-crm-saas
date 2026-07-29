from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.roles import PLATFORM_ADMIN, TENANT_ADMIN
from app.db.session import get_db
from app.models import Module, SaasPlan, Tenant, TenantModule, TenantSubscription, User
from app.schemas.subscription import ModuleOut, SaasPlanCreate, SaasPlanOut, TenantModuleIn, TenantModuleOut, TenantSubscriptionOut, TenantSubscriptionUpsert


router = APIRouter()

SUPPORTED_MODULES = {"core", "administration", "crm", "collections", "legal", "sales", "documents", "bi", "integrations", "hr", "finance", "industrial"}


def require_platform(user: User) -> None:
    if user.role != PLATFORM_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo IEP SuperAdmin puede administrar suscripciones.")


def ensure_subscription_read(user: User, tenant_id: int) -> None:
    if user.role == PLATFORM_ADMIN:
        return
    if user.role == TENANT_ADMIN and user.tenant_id == tenant_id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso a la suscripcion solicitada.")


def module_enabled_for_tenant(db: Session, tenant_id: int, module_code: str) -> bool:
    module = db.scalar(select(TenantModule).where(TenantModule.tenant_id == tenant_id, TenantModule.module_code == module_code))
    return True if module is None else bool(module.enabled and module.is_enabled)


@router.get("/modules", response_model=list[ModuleOut])
def list_modules(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[Module]:
    if user.role not in {PLATFORM_ADMIN, TENANT_ADMIN}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso a modulos SaaS.")
    return list(db.scalars(select(Module).order_by(Module.order, Module.name)))


@router.get("/plans", response_model=list[SaasPlanOut])
def list_plans(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[SaasPlan]:
    if user.role not in {PLATFORM_ADMIN, TENANT_ADMIN}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso a planes SaaS.")
    return list(db.scalars(select(SaasPlan).order_by(SaasPlan.monthly_price, SaasPlan.name)))


@router.post("/plans", response_model=SaasPlanOut, status_code=status.HTTP_201_CREATED)
def create_plan(payload: SaasPlanCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> SaasPlan:
    require_platform(user)
    plan = SaasPlan(**payload.model_dump())
    db.add(plan)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un plan con ese codigo.") from exc
    db.refresh(plan)
    return plan


@router.get("/tenant/{tenant_id}", response_model=TenantSubscriptionOut | None)
def get_tenant_subscription(tenant_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> TenantSubscription | None:
    ensure_subscription_read(user, tenant_id)
    return db.scalar(select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id).order_by(TenantSubscription.created_at.desc()))


@router.put("/tenant/{tenant_id}", response_model=TenantSubscriptionOut)
def upsert_tenant_subscription(tenant_id: int, payload: TenantSubscriptionUpsert, db: Session = Depends(get_db), user: User = Depends(current_user)) -> TenantSubscription:
    require_platform(user)
    if db.get(Tenant, tenant_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")
    if db.get(SaasPlan, payload.plan_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan no encontrado.")
    subscription = db.scalar(select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id).order_by(TenantSubscription.created_at.desc()))
    if subscription is None:
        subscription = TenantSubscription(tenant_id=tenant_id, **payload.model_dump())
        db.add(subscription)
    else:
        for field, value in payload.model_dump().items():
            setattr(subscription, field, value)
    db.commit()
    db.refresh(subscription)
    return subscription


@router.get("/modules/{tenant_id}", response_model=list[TenantModuleOut])
def list_tenant_modules(tenant_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[TenantModule]:
    ensure_subscription_read(user, tenant_id)
    return list(db.scalars(select(TenantModule).where(TenantModule.tenant_id == tenant_id).order_by(TenantModule.module_code)))


@router.put("/modules/{tenant_id}", response_model=list[TenantModuleOut])
def update_tenant_modules(tenant_id: int, payload: list[TenantModuleIn], db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[TenantModule]:
    require_platform(user)
    if db.get(Tenant, tenant_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")
    existing = {item.module_code: item for item in db.scalars(select(TenantModule).where(TenantModule.tenant_id == tenant_id))}
    for item in payload:
        if item.module_code not in SUPPORTED_MODULES:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Modulo no soportado: {item.module_code}.")
        module_def = db.scalar(select(Module).where(Module.code == item.module_code))
        module = existing.get(item.module_code)
        if module is None:
            module = TenantModule(
                tenant_id=tenant_id,
                module_id=module_def.id if module_def else None,
                module_code=item.module_code,
                enabled=item.enabled,
                is_enabled=item.enabled if item.is_enabled is None else item.is_enabled,
                configuration_json=item.configuration_json,
            )
            db.add(module)
        else:
            module.enabled = item.enabled
            module.is_enabled = item.enabled if item.is_enabled is None else item.is_enabled
            module.module_id = module_def.id if module_def else module.module_id
            module.configuration_json = item.configuration_json if item.configuration_json is not None else module.configuration_json
    db.commit()
    return list(db.scalars(select(TenantModule).where(TenantModule.tenant_id == tenant_id).order_by(TenantModule.module_code)))
