from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import AlertRule, BusinessRule, FunctionalCatalog, Tenant, User, WorkflowDefinition, WorkflowStage
from app.schemas.configuration import (
    AlertRuleCreate,
    AlertRuleOut,
    AlertRulePatch,
    BusinessRuleCreate,
    BusinessRuleOut,
    BusinessRulePatch,
    FunctionalCatalogCreate,
    FunctionalCatalogOut,
    FunctionalCatalogPatch,
    WorkflowCreate,
    WorkflowOut,
    WorkflowPatch,
    WorkflowStageCreate,
    WorkflowStageOut,
)
from app.services.access_control import is_platform_admin, require_permission, require_tenant
from app.services.audit_service import record_audit


router = APIRouter()


def _target_tenant_id(db: Session, user: User, requested_tenant_id: int | None) -> int | None:
    if is_platform_admin(db, user):
        if requested_tenant_id is None:
            return None
        tenant = db.get(Tenant, requested_tenant_id)
        if tenant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")
        return tenant.id
    tenant = require_tenant(db, user, requested_tenant_id)
    return tenant.id


def _scope_filter(model, user: User, db: Session, tenant_id: int | None):
    if is_platform_admin(db, user):
        if tenant_id is None:
            return True
        require_tenant(db, user, tenant_id)
        return or_(model.tenant_id.is_(None), model.tenant_id == tenant_id)
    tenant = require_tenant(db, user, tenant_id)
    return or_(model.tenant_id.is_(None), model.tenant_id == tenant.id)


def _ensure_patch_access(db: Session, user: User, tenant_id: int | None) -> None:
    if is_platform_admin(db, user):
        return
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo IEP SuperAdmin puede modificar plantillas globales.")
    require_tenant(db, user, tenant_id)


def _commit_or_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una configuracion con ese codigo en el alcance seleccionado.") from exc


@router.get("/catalogs", response_model=list[FunctionalCatalogOut])
def list_catalogs(
    module: str | None = None,
    catalog_type: str | None = None,
    tenant_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[FunctionalCatalog]:
    require_permission(db, user, "configuration.view")
    query = select(FunctionalCatalog).where(_scope_filter(FunctionalCatalog, user, db, tenant_id))
    if module:
        query = query.where(FunctionalCatalog.module == module)
    if catalog_type:
        query = query.where(FunctionalCatalog.catalog_type == catalog_type)
    return list(db.scalars(query.order_by(FunctionalCatalog.module, FunctionalCatalog.catalog_type, FunctionalCatalog.order, FunctionalCatalog.label)))


@router.post("/catalogs", response_model=FunctionalCatalogOut, status_code=status.HTTP_201_CREATED)
def create_catalog(payload: FunctionalCatalogCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> FunctionalCatalog:
    require_permission(db, user, "configuration.catalogs.manage")
    tenant_id = _target_tenant_id(db, user, payload.tenant_id)
    item = FunctionalCatalog(**payload.model_dump(exclude={"tenant_id"}), tenant_id=tenant_id)
    if not is_platform_admin(db, user):
        item.is_system = False
    db.add(item)
    db.flush()
    record_audit(db, user, "functional_catalog", "create", item.id, tenant_id, module="configuration", after={"module": item.module, "catalog_type": item.catalog_type, "code": item.code}, request=request)
    _commit_or_conflict(db)
    db.refresh(item)
    return item


@router.patch("/catalogs/{catalog_id}", response_model=FunctionalCatalogOut)
def patch_catalog(catalog_id: int, payload: FunctionalCatalogPatch, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> FunctionalCatalog:
    require_permission(db, user, "configuration.catalogs.manage")
    item = db.get(FunctionalCatalog, catalog_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalogo no encontrado.")
    _ensure_patch_access(db, user, item.tenant_id)
    updates = payload.model_dump(exclude_unset=True)
    if not is_platform_admin(db, user):
        updates.pop("is_system", None)
    for field, value in updates.items():
        setattr(item, field, value)
    record_audit(db, user, "functional_catalog", "update", item.id, item.tenant_id, module="configuration", after=updates, request=request)
    _commit_or_conflict(db)
    db.refresh(item)
    return item


@router.get("/rules", response_model=list[BusinessRuleOut])
def list_rules(module: str | None = None, rule_type: str | None = None, tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[BusinessRule]:
    require_permission(db, user, "configuration.view")
    query = select(BusinessRule).where(_scope_filter(BusinessRule, user, db, tenant_id))
    if module:
        query = query.where(BusinessRule.module == module)
    if rule_type:
        query = query.where(BusinessRule.rule_type == rule_type)
    return list(db.scalars(query.order_by(BusinessRule.module, BusinessRule.rule_type, BusinessRule.name)))


@router.post("/rules", response_model=BusinessRuleOut, status_code=status.HTTP_201_CREATED)
def create_rule(payload: BusinessRuleCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> BusinessRule:
    require_permission(db, user, "configuration.rules.manage")
    tenant_id = _target_tenant_id(db, user, payload.tenant_id)
    item = BusinessRule(**payload.model_dump(exclude={"tenant_id"}), tenant_id=tenant_id)
    db.add(item)
    db.flush()
    record_audit(db, user, "business_rule", "create", item.id, tenant_id, module="configuration", after={"module": item.module, "rule_type": item.rule_type, "code": item.code}, request=request)
    _commit_or_conflict(db)
    db.refresh(item)
    return item


@router.patch("/rules/{rule_id}", response_model=BusinessRuleOut)
def patch_rule(rule_id: int, payload: BusinessRulePatch, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> BusinessRule:
    require_permission(db, user, "configuration.rules.manage")
    item = db.get(BusinessRule, rule_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regla no encontrada.")
    _ensure_patch_access(db, user, item.tenant_id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(item, field, value)
    record_audit(db, user, "business_rule", "update", item.id, item.tenant_id, module="configuration", after=updates, request=request)
    _commit_or_conflict(db)
    db.refresh(item)
    return item


@router.get("/alert-rules", response_model=list[AlertRuleOut])
def list_alert_rules(module: str | None = None, tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[AlertRule]:
    require_permission(db, user, "configuration.view")
    query = select(AlertRule).where(_scope_filter(AlertRule, user, db, tenant_id))
    if module:
        query = query.where(AlertRule.module == module)
    return list(db.scalars(query.order_by(AlertRule.module, AlertRule.severity.desc(), AlertRule.name)))


@router.post("/alert-rules", response_model=AlertRuleOut, status_code=status.HTTP_201_CREATED)
def create_alert_rule(payload: AlertRuleCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> AlertRule:
    require_permission(db, user, "configuration.alerts.manage")
    tenant_id = _target_tenant_id(db, user, payload.tenant_id)
    item = AlertRule(**payload.model_dump(exclude={"tenant_id"}), tenant_id=tenant_id)
    db.add(item)
    db.flush()
    record_audit(db, user, "alert_rule", "create", item.id, tenant_id, module="configuration", after={"module": item.module, "code": item.code}, request=request)
    _commit_or_conflict(db)
    db.refresh(item)
    return item


@router.patch("/alert-rules/{rule_id}", response_model=AlertRuleOut)
def patch_alert_rule(rule_id: int, payload: AlertRulePatch, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> AlertRule:
    require_permission(db, user, "configuration.alerts.manage")
    item = db.get(AlertRule, rule_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta configurable no encontrada.")
    _ensure_patch_access(db, user, item.tenant_id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(item, field, value)
    record_audit(db, user, "alert_rule", "update", item.id, item.tenant_id, module="configuration", after=updates, request=request)
    _commit_or_conflict(db)
    db.refresh(item)
    return item


@router.get("/workflows", response_model=list[WorkflowOut])
def list_workflows(module: str | None = None, tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[WorkflowDefinition]:
    require_permission(db, user, "configuration.view")
    query = select(WorkflowDefinition).where(_scope_filter(WorkflowDefinition, user, db, tenant_id))
    if module:
        query = query.where(WorkflowDefinition.module == module)
    return list(db.scalars(query.order_by(WorkflowDefinition.module, WorkflowDefinition.name)))


@router.post("/workflows", response_model=WorkflowOut, status_code=status.HTTP_201_CREATED)
def create_workflow(payload: WorkflowCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> WorkflowDefinition:
    require_permission(db, user, "configuration.workflows.manage")
    tenant_id = _target_tenant_id(db, user, payload.tenant_id)
    item = WorkflowDefinition(**payload.model_dump(exclude={"tenant_id"}), tenant_id=tenant_id)
    db.add(item)
    db.flush()
    record_audit(db, user, "workflow", "create", item.id, tenant_id, module="configuration", after={"module": item.module, "code": item.code}, request=request)
    _commit_or_conflict(db)
    db.refresh(item)
    return item


@router.patch("/workflows/{workflow_id}", response_model=WorkflowOut)
def patch_workflow(workflow_id: int, payload: WorkflowPatch, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> WorkflowDefinition:
    require_permission(db, user, "configuration.workflows.manage")
    item = db.get(WorkflowDefinition, workflow_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow no encontrado.")
    _ensure_patch_access(db, user, item.tenant_id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(item, field, value)
    record_audit(db, user, "workflow", "update", item.id, item.tenant_id, module="configuration", after=updates, request=request)
    _commit_or_conflict(db)
    db.refresh(item)
    return item


@router.get("/workflows/{workflow_id}/stages", response_model=list[WorkflowStageOut])
def list_workflow_stages(workflow_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[WorkflowStage]:
    require_permission(db, user, "configuration.view")
    workflow = db.get(WorkflowDefinition, workflow_id)
    if workflow is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow no encontrado.")
    if not is_platform_admin(db, user) and workflow.tenant_id not in {None, user.tenant_id}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Workflow fuera de tu empresa.")
    return list(db.scalars(select(WorkflowStage).where(WorkflowStage.workflow_id == workflow_id).order_by(WorkflowStage.order, WorkflowStage.name)))


@router.post("/workflows/{workflow_id}/stages", response_model=WorkflowStageOut, status_code=status.HTTP_201_CREATED)
def create_workflow_stage(workflow_id: int, payload: WorkflowStageCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(current_user)) -> WorkflowStage:
    require_permission(db, user, "configuration.workflows.manage")
    workflow = db.get(WorkflowDefinition, workflow_id)
    if workflow is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow no encontrado.")
    _ensure_patch_access(db, user, workflow.tenant_id)
    item = WorkflowStage(workflow_id=workflow.id, **payload.model_dump())
    db.add(item)
    db.flush()
    record_audit(db, user, "workflow_stage", "create", item.id, workflow.tenant_id, module="configuration", after={"workflow_id": workflow.id, "code": item.code}, request=request)
    _commit_or_conflict(db)
    db.refresh(item)
    return item
