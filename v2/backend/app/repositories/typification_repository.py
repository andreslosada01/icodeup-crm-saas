from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import TypificationNode


class TypificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, tenant_id: int) -> list[TypificationNode]:
        query = (
            select(TypificationNode)
            .where(TypificationNode.tenant_id == tenant_id)
            .order_by(TypificationNode.sort_order, TypificationNode.label)
        )
        return list(self.db.scalars(query))

    def create(self, payload: dict) -> TypificationNode:
        node = TypificationNode(**payload)
        self.db.add(node)
        self.db.flush()
        return node

