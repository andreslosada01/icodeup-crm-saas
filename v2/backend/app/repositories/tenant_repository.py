from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Tenant


class TenantRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Tenant]:
        return list(self.db.scalars(select(Tenant).order_by(Tenant.name)))

    def get_by_slug(self, slug: str) -> Tenant | None:
        return self.db.scalar(select(Tenant).where(Tenant.slug == slug))

    def create(self, name: str, slug: str, tax_id: str | None = None) -> Tenant:
        tenant = Tenant(name=name, slug=slug, tax_id=tax_id)
        self.db.add(tenant)
        self.db.flush()
        return tenant

