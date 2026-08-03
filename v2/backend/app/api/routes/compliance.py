from __future__ import annotations

import json
import math
import re

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.api.routes.crm.access import customer_for_access
from app.api.routes.crm.obligations import obligation_for_access
from app.db.session import get_db
from app.models import BusinessRule, Project, Tenant, User
from app.schemas.compliance import (
    ContactEvaluationOut,
    ContactEvaluationRequest,
    ContactRuleCreate,
    ContactRuleListResponse,
    ContactRuleOut,
    ContactRulePatch,
    ContactStatusOut,
)
from app.services.access_control import is_platform_admin, require_module, require_permission, require_tenant, user_has_permission
from app.services.audit_service import record_audit
from app.services.contact_compliance import (
    CONTACT_PAGE_SIZE,
    CONTACT_RULE_MODULE,
    CONTACT_RULE_TYPE,
    contact_rule_action,
    contact_rule_condition,
    contact_rule_to_dict,
    evaluate_contact_rules,
    customer_contact_status,
    json_dict,
    normalize_channel,
)


router = APIRouter()


def _target_tenant_id(db: Session, user: User, tenant_id: int | None) -> int | None:
    if is_platform_admin(db, user):
        if tenant_id is None:
            return None
        tenant = db.get(Tenant, tenant_id)
        if tenant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")
        return tenant.id
    tenant = require_tenant(db, user, tenant_id)
    return tenant.id


def _rule_access(db: Session, user: User, item: BusinessRule, write: bool = False) -> None:
    if item.module != CONTACT_RULE_MODULE or item.rule_type != CONTACT_RULE_TYPE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regla de contacto no encontrada.")
    if is_platform_admin(db, user):
        return
    if item.tenant_id is None:
        if write:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo IEP SuperAdmin puede modificar reglas globales.")
        return
    require_tenant(db, user, item.tenant_id)


def _validate_project_scope(db: Session, tenant_id: int | None, project_id: int | None) -> None:
    if not project_id:
        return
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Una regla por cartera debe estar asociada a una empresa.")
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cartera no encontrada.")
    if project.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La cartera no pertenece a la empresa de la regla.")


def _slug_code(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").upper()
    return (text or "CONTACT_RULE")[:110]


def _commit_or_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una regla con ese codigo en el alcance seleccionado.") from exc


@router.get("/contact-rules", response_model=ContactRuleListResponse)
def list_contact_rules(
    tenant_id: int | None = None,
    project_id: int | None = None,
    active_only: bool = False,
    page: int = 1,
    page_size: int = Query(default=CONTACT_PAGE_SIZE, ge=1, le=CONTACT_PAGE_SIZE),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> ContactRuleListResponse:
    require_module(db, user, "collections", tenant_id)
    require_permission(db, user, "contact_compliance.view")
    target_tenant_id = _target_tenant_id(db, user, tenant_id)
    query = select(BusinessRule).where(BusinessRule.module == CONTACT_RULE_MODULE, BusinessRule.rule_type == CONTACT_RULE_TYPE)
    if target_tenant_id is None and is_platform_admin(db, user):
        pass
    else:
        target_tenant_id = target_tenant_id or user.tenant_id
        query = query.where(or_(BusinessRule.tenant_id.is_(None), BusinessRule.tenant_id == target_tenant_id))
    if active_only:
        query = query.where(BusinessRule.is_active.is_(True))
    rules = [contact_rule_to_dict(item) for item in db.scalars(query.order_by(BusinessRule.is_active.desc(), BusinessRule.name))]
    if project_id:
        rules = [item for item in rules if item["project_id"] in {None, project_id}]
    rules.sort(key=lambda item: (item["priority"], item["name"]))
    page = max(1, page)
    page_size = min(CONTACT_PAGE_SIZE, max(1, page_size))
    total = len(rules)
    offset = (page - 1) * page_size
    return ContactRuleListResponse(items=rules[offset:offset + page_size], total=total, page=page, page_size=page_size, total_pages=max(1, math.ceil(total / page_size)))


@router.post("/contact-rules", response_model=ContactRuleOut, status_code=status.HTTP_201_CREATED)
def create_contact_rule(payload: ContactRuleCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_module(db, user, "collections", payload.tenant_id)
    require_permission(db, user, "contact_compliance.manage")
    tenant_id = _target_tenant_id(db, user, payload.tenant_id)
    _validate_project_scope(db, tenant_id, payload.project_id)
    item = BusinessRule(
        tenant_id=tenant_id,
        module=CONTACT_RULE_MODULE,
        rule_type=CONTACT_RULE_TYPE,
        code=(payload.code or _slug_code(payload.name)),
        name=payload.name.strip(),
        description=payload.description,
        condition_json=json.dumps(contact_rule_condition(payload), ensure_ascii=True),
        action_json=json.dumps(contact_rule_action(payload), ensure_ascii=True),
        severity=payload.severity,
        is_active=payload.is_active,
    )
    db.add(item)
    db.flush()
    record_audit(db, user, "contact_rule", "create", item.id, tenant_id, module="collections", after=contact_rule_to_dict(item), request=request)
    _commit_or_conflict(db)
    db.refresh(item)
    return contact_rule_to_dict(item)


@router.patch("/contact-rules/{rule_id}", response_model=ContactRuleOut)
def patch_contact_rule(rule_id: int, payload: ContactRulePatch, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "contact_compliance.manage")
    item = db.get(BusinessRule, rule_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regla de contacto no encontrada.")
    _rule_access(db, user, item, write=True)
    require_module(db, user, "collections", item.tenant_id)
    updates = payload.model_dump(exclude_unset=True)
    before = contact_rule_to_dict(item)
    if "project_id" in updates:
        _validate_project_scope(db, item.tenant_id, updates["project_id"])
    if "code" in updates and updates["code"]:
        item.code = updates["code"]
    if "name" in updates and updates["name"]:
        item.name = updates["name"].strip()
    if "description" in updates:
        item.description = updates["description"]
    if "severity" in updates and updates["severity"]:
        item.severity = updates["severity"]
    if "is_active" in updates:
        item.is_active = bool(updates["is_active"])
    condition = json_dict(item.condition_json)
    action = json_dict(item.action_json)
    condition_fields = set(contact_rule_condition(ContactRuleCreate(name=item.name)).keys())
    action_fields = {"severity", "recommended_action", "priority"}
    for key, value in updates.items():
        if key in condition_fields:
            if key in {"channels", "blocked_channels"} and value is not None:
                value = [normalize_channel(item_value) for item_value in value]
            condition[key] = value
        if key in action_fields:
            action[key] = value
    item.condition_json = json.dumps(condition, ensure_ascii=True)
    item.action_json = json.dumps(action, ensure_ascii=True)
    record_audit(db, user, "contact_rule", "update", item.id, item.tenant_id, module="collections", before=before, after=contact_rule_to_dict(item), request=request)
    _commit_or_conflict(db)
    db.refresh(item)
    return contact_rule_to_dict(item)


@router.post("/contact-rules/{rule_id}/toggle", response_model=ContactRuleOut)
def toggle_contact_rule(rule_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "contact_compliance.manage")
    item = db.get(BusinessRule, rule_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regla de contacto no encontrada.")
    _rule_access(db, user, item, write=True)
    require_module(db, user, "collections", item.tenant_id)
    before = {"is_active": item.is_active}
    item.is_active = not item.is_active
    record_audit(db, user, "contact_rule", "toggle", item.id, item.tenant_id, module="collections", before=before, after={"is_active": item.is_active}, request=request)
    db.commit()
    db.refresh(item)
    return contact_rule_to_dict(item)


@router.post("/evaluate-contact", response_model=ContactEvaluationOut)
def evaluate_contact(payload: ContactEvaluationRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_module(db, user, "collections", payload.tenant_id)
    require_permission(db, user, "contact_compliance.evaluate")
    customer = customer_for_access(db, payload.customer_id, user, write=False)
    if payload.tenant_id and payload.tenant_id != customer.tenant_id and not is_platform_admin(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cliente fuera de la empresa solicitada.")
    obligation = obligation_for_access(db, payload.obligation_id, user, write=False) if payload.obligation_id else None
    if obligation and obligation.customer_id != customer.id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La obligacion no pertenece al cliente seleccionado.")
    decision = evaluate_contact_rules(
        db,
        user=user,
        customer=customer,
        obligation=obligation,
        channel=payload.channel,
        current_at=payload.current_at,
        source=payload.source or "evaluate_contact",
        audit=True,
        request=request,
    )
    db.commit()
    return decision


@router.get("/customer/{customer_id}/contact-status", response_model=ContactStatusOut)
def get_customer_contact_status(customer_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    if not user_has_permission(db, user, "contact_compliance.view"):
        require_permission(db, user, "contact_compliance.evaluate")
    require_module(db, user, "collections")
    customer = customer_for_access(db, customer_id, user, write=False)
    return customer_contact_status(db, user, customer)
