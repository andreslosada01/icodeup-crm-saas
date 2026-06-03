"""sprint1_obligation_links

Revision ID: 20260603_0004
Revises: 20260603_0003
Create Date: 2026-06-03

Migracion no destructiva para enlazar gestiones, promesas y acuerdos a obligaciones.
"""

from __future__ import annotations

from alembic import op


revision = "20260603_0004"
down_revision = "20260603_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE IF EXISTS management_activities ADD COLUMN IF NOT EXISTS obligation_id INTEGER REFERENCES customer_obligations(id)")
    op.execute("ALTER TABLE IF EXISTS payment_promises ADD COLUMN IF NOT EXISTS obligation_id INTEGER REFERENCES customer_obligations(id)")
    op.execute("ALTER TABLE IF EXISTS payment_agreements ADD COLUMN IF NOT EXISTS obligation_id INTEGER REFERENCES customer_obligations(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_management_activities_obligation_id ON management_activities (obligation_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_payment_promises_obligation_id ON payment_promises (obligation_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_payment_agreements_obligation_id ON payment_agreements (obligation_id)")


def downgrade() -> None:
    # Migracion no destructiva: no se eliminan columnas ni indices para proteger datos operativos.
    pass
