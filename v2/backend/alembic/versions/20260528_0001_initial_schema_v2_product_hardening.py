"""initial_schema_v2_product_hardening

Revision ID: 20260528_0001
Revises:
Create Date: 2026-05-28

Baseline no destructiva para el esquema V2 actual. Usa la metadata vigente
del producto hardening para crear tablas faltantes en bases nuevas y conserva
datos/tablas existentes en ambientes ya inicializados.
"""

from __future__ import annotations

from alembic import op

from app.db.session import Base
from app.models import audit, configuration, crm, documents, identity, legal, menu, party, sales, security, subscription, tenant  # noqa: F401


revision = "20260528_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True)


def downgrade() -> None:
    # Baseline no destructiva: no se eliminan tablas ni columnas.
    pass
