"""operational_sheet_rows

Revision ID: 20260603_0003
Revises: 20260603_0002
Create Date: 2026-06-03

Migracion no destructiva para la hoja operativa persistente de Mi Excel Web.
"""

from __future__ import annotations

from alembic import op

from app.db.session import Base
from app.models import collection_ops  # noqa: F401


revision = "20260603_0003"
down_revision = "20260603_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.tables["operational_sheet_rows"].create(bind=bind, checkfirst=True)


def downgrade() -> None:
    # Migracion no destructiva: no se eliminan tablas ni datos.
    pass
