from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import Project, Tenant, TypificationCombinationRule, TypificationNode, TypificationTree, TypificationTreeNode, User
from app.repositories.typification_repository import TypificationRepository
from app.schemas.collection_ops import (
    TypificationCombinationCreate,
    TypificationCombinationOut,
    TypificationCombinationValidate,
    TypificationTreeCreate,
    TypificationTreeNodeCreate,
    TypificationTreeNodeOut,
    TypificationTreeNodeUpdate,
    TypificationTreeOut,
    TypificationTreeUpdate,
)
from app.schemas.typification import TypificationCreate, TypificationOut, TypificationUpdate
from app.services.access_control import is_platform_admin, require_permission, require_tenant


router = APIRouter()


def _tenant_id_for_payload(db: Session, user: User, payload_tenant_id: int | None = None) -> int:
    tenant = require_tenant(db, user, payload_tenant_id)
    return tenant.id


def _ensure_project_scope(db: Session, user: User, tenant_id: int, project_id: int | None) -> None:
    if project_id is None:
        return
    project = db.get(Project, project_id)
    if project is None or project.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Proyecto fuera de la empresa.")


def _tree_for_access(db: Session, tree_id: int, user: User, write: bool = False) -> TypificationTree:
    tree = db.get(TypificationTree, tree_id)
    if tree is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arbol de tipificacion no encontrado.")
    if not is_platform_admin(db, user) and tree.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Arbol fuera de tu empresa.")
    if write:
        require_permission(db, user, "typifications.trees.manage")
    return tree


def _combination_to_out(item: TypificationCombinationRule) -> TypificationCombinationOut:
    return TypificationCombinationOut(
        id=item.id,
        tenant_id=item.tenant_id,
        project_id=item.project_id,
        tree_id=item.tree_id,
        path=json.loads(item.path_json or "[]"),
        required_fields=json.loads(item.required_fields_json or "{}"),
        effects=json.loads(item.effects_json or "{}"),
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("", response_model=list[TypificationOut])
def list_typifications(tenant_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list:
    require_permission(db, user, "typifications.view")
    resolved_tenant_id = _tenant_id_for_payload(db, user, tenant_id)
    return TypificationRepository(db).list(resolved_tenant_id)


@router.post("", response_model=TypificationOut)
def create_typification(payload: TypificationCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    require_permission(db, user, "typifications.manage")
    _tenant_id_for_payload(db, user, payload.tenant_id)
    _ensure_project_scope(db, user, payload.tenant_id, payload.project_id)
    node = TypificationRepository(db).create(payload.model_dump())
    db.commit()
    db.refresh(node)
    return node


@router.patch("/{node_id}", response_model=TypificationOut)
def update_typification(node_id: int, payload: TypificationUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    require_permission(db, user, "typifications.manage")
    node = db.get(TypificationNode, node_id)
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipificacion no encontrada.")
    if not is_platform_admin(db, user) and node.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tipificacion fuera de tu empresa.")
    updates = payload.model_dump(exclude_unset=True)
    if updates.get("parent_id") == node.id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Una tipificacion no puede ser su propio padre.")
    _ensure_project_scope(db, user, node.tenant_id, updates.get("project_id", node.project_id))
    for field, value in updates.items():
        setattr(node, field, value)
    db.commit()
    db.refresh(node)
    return node


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_typification(node_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    require_permission(db, user, "typifications.manage")
    node = db.get(TypificationNode, node_id)
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipificacion no encontrada.")
    if not is_platform_admin(db, user) and node.tenant_id != user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tipificacion fuera de tu empresa.")
    child = db.scalar(select(TypificationNode).where(TypificationNode.parent_id == node.id))
    if child:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede eliminar una tipificacion con hijos.")
    db.delete(node)
    db.commit()


@router.get("/trees", response_model=list[TypificationTreeOut])
def list_trees(
    tenant_id: int | None = None,
    module: str | None = None,
    project_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[TypificationTree]:
    require_permission(db, user, "typifications.view")
    query = select(TypificationTree).order_by(TypificationTree.module, TypificationTree.name)
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(TypificationTree.tenant_id == tenant_id)
    else:
        query = query.where(TypificationTree.tenant_id == user.tenant_id)
    if module:
        query = query.where(TypificationTree.module == module)
    if project_id:
        query = query.where((TypificationTree.project_id == project_id) | (TypificationTree.project_id.is_(None)))
    return list(db.scalars(query))


@router.post("/trees", response_model=TypificationTreeOut, status_code=status.HTTP_201_CREATED)
def create_tree(payload: TypificationTreeCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> TypificationTree:
    require_permission(db, user, "typifications.trees.manage")
    tenant_id = _tenant_id_for_payload(db, user, payload.tenant_id)
    _ensure_project_scope(db, user, tenant_id, payload.project_id)
    existing = db.scalar(
        select(TypificationTree).where(
            TypificationTree.tenant_id == tenant_id,
            TypificationTree.project_id == payload.project_id,
            TypificationTree.module == payload.module,
            TypificationTree.code == payload.code,
        )
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un arbol con ese codigo.")
    tree = TypificationTree(**payload.model_dump(exclude={"tenant_id"}), tenant_id=tenant_id)
    db.add(tree)
    db.commit()
    db.refresh(tree)
    return tree


@router.patch("/trees/{tree_id}", response_model=TypificationTreeOut)
def update_tree(tree_id: int, payload: TypificationTreeUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> TypificationTree:
    tree = _tree_for_access(db, tree_id, user, write=True)
    updates = payload.model_dump(exclude_unset=True)
    _ensure_project_scope(db, user, tree.tenant_id, updates.get("project_id", tree.project_id))
    for field, value in updates.items():
        setattr(tree, field, value)
    db.commit()
    db.refresh(tree)
    return tree


@router.get("/trees/{tree_id}/nodes", response_model=list[TypificationTreeNodeOut])
def list_tree_nodes(tree_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[TypificationTreeNode]:
    require_permission(db, user, "typifications.view")
    _tree_for_access(db, tree_id, user)
    return list(db.scalars(select(TypificationTreeNode).where(TypificationTreeNode.tree_id == tree_id).order_by(TypificationTreeNode.level, TypificationTreeNode.order, TypificationTreeNode.label)))


@router.post("/trees/{tree_id}/nodes", response_model=TypificationTreeNodeOut, status_code=status.HTTP_201_CREATED)
def create_tree_node(tree_id: int, payload: TypificationTreeNodeCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> TypificationTreeNode:
    _tree_for_access(db, tree_id, user, write=True)
    if payload.parent_id:
        parent = db.get(TypificationTreeNode, payload.parent_id)
        if parent is None or parent.tree_id != tree_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Nodo padre fuera del arbol.")
    node = TypificationTreeNode(tree_id=tree_id, **payload.model_dump())
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


@router.patch("/nodes/{node_id}", response_model=TypificationTreeNodeOut)
def update_tree_node(node_id: int, payload: TypificationTreeNodeUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> TypificationTreeNode:
    node = db.get(TypificationTreeNode, node_id)
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nodo no encontrado.")
    _tree_for_access(db, node.tree_id, user, write=True)
    updates = payload.model_dump(exclude_unset=True)
    if updates.get("parent_id") == node.id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Un nodo no puede ser padre de si mismo.")
    for field, value in updates.items():
        setattr(node, field, value)
    db.commit()
    db.refresh(node)
    return node


@router.get("/combinations", response_model=list[TypificationCombinationOut])
def list_combinations(
    tenant_id: int | None = None,
    tree_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[TypificationCombinationOut]:
    require_permission(db, user, "typifications.view")
    query = select(TypificationCombinationRule).order_by(TypificationCombinationRule.created_at.desc())
    if is_platform_admin(db, user):
        if tenant_id:
            query = query.where(TypificationCombinationRule.tenant_id == tenant_id)
    else:
        query = query.where(TypificationCombinationRule.tenant_id == user.tenant_id)
    if tree_id:
        query = query.where(TypificationCombinationRule.tree_id == tree_id)
    return [_combination_to_out(item) for item in db.scalars(query)]


@router.post("/combinations", response_model=TypificationCombinationOut, status_code=status.HTTP_201_CREATED)
def create_combination(payload: TypificationCombinationCreate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> TypificationCombinationOut:
    require_permission(db, user, "typifications.combinations.manage")
    tree = _tree_for_access(db, payload.tree_id, user, write=False)
    tenant_id = _tenant_id_for_payload(db, user, payload.tenant_id or tree.tenant_id)
    if tenant_id != tree.tenant_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Combinacion fuera del tenant del arbol.")
    rule = TypificationCombinationRule(
        tenant_id=tenant_id,
        project_id=payload.project_id if payload.project_id is not None else tree.project_id,
        tree_id=payload.tree_id,
        path_json=json.dumps(payload.path),
        required_fields_json=json.dumps(payload.required_fields),
        effects_json=json.dumps(payload.effects),
        is_active=payload.is_active,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return _combination_to_out(rule)


@router.post("/validate-combination")
def validate_combination(payload: TypificationCombinationValidate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    require_permission(db, user, "typifications.view")
    _tree_for_access(db, payload.tree_id, user)
    path_as_text = json.dumps(payload.path)
    rules = list(db.scalars(select(TypificationCombinationRule).where(TypificationCombinationRule.tree_id == payload.tree_id, TypificationCombinationRule.is_active.is_(True))))
    matched = next((rule for rule in rules if rule.path_json == path_as_text), None)
    required_fields = json.loads(matched.required_fields_json or "{}") if matched else {}
    effects = json.loads(matched.effects_json or "{}") if matched else {}
    missing = [field for field, required in required_fields.items() if required and not payload.payload.get(field)]
    return {
        "valid": matched is not None and not missing,
        "matched_rule_id": matched.id if matched else None,
        "missing_fields": missing,
        "effects": effects,
        "message": "Combinacion valida." if matched and not missing else "Combinacion incompleta o no permitida.",
    }
