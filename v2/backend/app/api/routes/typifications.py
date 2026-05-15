from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_platform_admin
from app.db.session import get_db
from app.models import TypificationNode
from app.repositories.typification_repository import TypificationRepository
from app.schemas.typification import TypificationCreate, TypificationOut, TypificationUpdate


router = APIRouter(dependencies=[Depends(require_platform_admin)])


@router.get("", response_model=list[TypificationOut])
def list_typifications(tenant_id: int, db: Session = Depends(get_db)) -> list:
    return TypificationRepository(db).list(tenant_id)


@router.post("", response_model=TypificationOut)
def create_typification(payload: TypificationCreate, db: Session = Depends(get_db)):
    node = TypificationRepository(db).create(payload.model_dump())
    db.commit()
    db.refresh(node)
    return node


@router.patch("/{node_id}", response_model=TypificationOut)
def update_typification(node_id: int, payload: TypificationUpdate, db: Session = Depends(get_db)):
    node = db.get(TypificationNode, node_id)
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipificacion no encontrada.")
    updates = payload.model_dump(exclude_unset=True)
    if updates.get("parent_id") == node.id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Una tipificacion no puede ser su propio padre.")
    for field, value in updates.items():
        setattr(node, field, value)
    db.commit()
    db.refresh(node)
    return node


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_typification(node_id: int, db: Session = Depends(get_db)):
    node = db.get(TypificationNode, node_id)
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipificacion no encontrada.")
    child = db.scalar(select(TypificationNode).where(TypificationNode.parent_id == node.id))
    if child:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede eliminar una tipificacion con hijos.")
    db.delete(node)
    db.commit()
